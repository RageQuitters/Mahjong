import os
import gc
import torch
from PIL import Image
import torchvision.transforms as T
import torch.nn.functional as F
import cv2
import numpy as np

from backend.vision.model import TileCNN

# =============================================================================
# CONFIGURATION
# =============================================================================

IMAGE_SIZE = 128
MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")

MODEL_FILES = {
    "group":      "layer1_group.pth",
    "suit_type":  "layer2_suit_type.pth",
    "honor_type": "layer2_honor_type.pth",
    "bonus_type": "layer2_bonus_type.pth",
    "char":       "layer3_char.pth",
    "bam":        "layer3_bam.pth",
    "dot":        "layer3_dot.pth",
    "wind":       "layer3_wind.pth",
    "dragon":     "layer3_dragon.pth",
}

# GradCAM — flip to True when debugging
ENABLE_GRADCAM = False
ACT_MAP_DIR    = "activation_maps"

# =============================================================================
# DEVICE + TRANSFORM
# =============================================================================

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

transform = T.Compose([
    T.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    T.ToTensor(),
])

# =============================================================================
# LAZY MODEL LOADING
# =============================================================================

_models = {}  # populated on first use

def _load_model(key):
    path = os.path.join(MODELS_DIR, MODEL_FILES[key])
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model not found: {path}")
    checkpoint = torch.load(path, map_location=device, weights_only=False)
    model      = TileCNN(checkpoint["num_classes"]).to(device)
    model.load_state_dict(checkpoint["model_state"])
    model.eval()
    return model, checkpoint["classes"]


def _get_model(key):
    if key not in _models:
        _models[key] = _load_model(key)
    return _models[key]

# =============================================================================
# GRADCAM
# =============================================================================

def _get_last_conv(model):
    last = None
    for m in model.modules():
        if isinstance(m, torch.nn.Conv2d):
            last = m
    return last


def _save_gradcam(tile_bgr, img_tensor, model, pred_idx, tile_id, suffix):
    print(f"generating GradCAM for {suffix} (pred idx: {pred_idx})...")
    layer = _get_last_conv(model)
    if layer is None:
        return

    feat_box = [None]
    grad_box = [None]

    h1 = layer.register_forward_hook(lambda m, i, o: feat_box.__setitem__(0, o))
    h2 = layer.register_backward_hook(lambda m, i, o: grad_box.__setitem__(0, o[0]))

    model.zero_grad()
    logits = model(img_tensor)
    logits[0, pred_idx].backward()

    features  = feat_box[0]
    gradients = grad_box[0]

    pooled = gradients.mean(dim=[0, 2, 3])
    cam    = torch.zeros(features.shape[2:], device=features.device)
    for i, w in enumerate(pooled):
        cam += w * features[0, i]

    cam  = F.relu(cam)
    cam -= cam.min()
    cam /= (cam.max() + 1e-8)
    cam  = cam.detach().cpu().numpy()
    cam  = cv2.resize(cam, (tile_bgr.shape[1], tile_bgr.shape[0]))

    heatmap = cv2.applyColorMap(np.uint8(255 * cam), cv2.COLORMAP_JET)
    overlay = cv2.addWeighted(tile_bgr, 0.6, heatmap, 0.4, 0)

    os.makedirs(ACT_MAP_DIR, exist_ok=True)
    cv2.imwrite(os.path.join(ACT_MAP_DIR, f"{tile_id}_{suffix}_pred{pred_idx}.png"), overlay)

    h1.remove()
    h2.remove()

    # clean up gradcam tensors
    del logits, features, gradients, pooled, cam, heatmap, overlay

# =============================================================================
# INFERENCE HELPERS
# =============================================================================

def _preprocess(tile_bgr):
    img_rgb = tile_bgr[:, :, ::-1].copy()
    img     = Image.fromarray(img_rgb).convert("RGB")
    tensor  = transform(img).unsqueeze(0).to(device)
    del img_rgb, img
    return tensor


def _predict(key, img_tensor):
    model, classes = _get_model(key)
    with torch.no_grad():
        logits = model(img_tensor)
    idx = logits.argmax(dim=1).item()
    label = classes[idx]
    del logits
    return idx, label

# =============================================================================
# PUBLIC API
# =============================================================================

def classify_tile_image(tile_bgr, tile_id="tile"):
    """
    3-layer hierarchical classification.

    Layer 1 : group      → suit | honor | bonus
    Layer 2 : suit_type  → char | bam | dot        (if suit)
              honor_type → wind | dragon            (if honor)
              bonus_type → animal | flower          (if bonus)
    Layer 3 : char/bam/dot → 1-9                   (if suit)
              wind       → EAST/SOUTH/WEST/NORTH    (if honor+wind)
              dragon     → RED/GREEN/WHITE_DRAGON   (if honor+dragon)

    Args:
        tile_bgr (np.ndarray): cropped BGR tile image from YOLO
        tile_id  (str):        identifier for GradCAM filenames

    Returns:
        str: predicted class name (e.g. "3_BAM", "EAST", "GREEN_DRAGON", "animal")
    """
    img = _preprocess(tile_bgr)
    try:
        # ------------------------------------------------------------------
        # Layer 1 — group
        # ------------------------------------------------------------------
        group_idx, group = _predict("group", img)

        if ENABLE_GRADCAM:
            model, _ = _get_model("group")
            _save_gradcam(tile_bgr, img, model, group_idx, tile_id, "L1_group")

        # ------------------------------------------------------------------
        # Layer 2
        # ------------------------------------------------------------------
        if group == "honor":
            l2_idx, honor_type = _predict("honor_type", img)
            if ENABLE_GRADCAM:
                model, _ = _get_model("honor_type")
                _save_gradcam(tile_bgr, img, model, l2_idx, tile_id, "L2_honor_type")

            l3_idx, label = _predict(honor_type, img)
            if ENABLE_GRADCAM:
                model, _ = _get_model(honor_type)
                _save_gradcam(tile_bgr, img, model, l3_idx, tile_id, f"L3_{honor_type}")

        elif group == "suit":
            l2_idx, suit_type = _predict("suit_type", img)
            if ENABLE_GRADCAM:
                model, _ = _get_model("suit_type")
                _save_gradcam(tile_bgr, img, model, l2_idx, tile_id, "L2_suit_type")

            l3_idx, label = _predict(suit_type, img)
            if ENABLE_GRADCAM:
                model, _ = _get_model(suit_type)
                _save_gradcam(tile_bgr, img, model, l3_idx, tile_id, f"L3_{suit_type}")

        else:  # bonus
            l2_idx, bonus_type = _predict("bonus_type", img)
            if ENABLE_GRADCAM:
                model, _ = _get_model("bonus_type")
                _save_gradcam(tile_bgr, img, model, l2_idx, tile_id, "L2_bonus_type")
            label = bonus_type

    finally:
        # always free the input tensor even if an exception occurs
        del img
        gc.collect()
        torch.cuda.empty_cache()
    return label