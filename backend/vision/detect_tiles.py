from ultralytics import YOLO
import os

CONF_THRESH = 0.5
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "detection",
                          "runs",
                          "detect",
                          "train4",
                          "weights",
                          "best.pt")


# Load once
_model = YOLO(MODEL_PATH)

def detect_tiles(image_bgr):
    """
    Args:
        image_bgr (np.ndarray): full-resolution BGR image

    Returns:
        List[tuple]: [(x1, y1, x2, y2), ...] in pixel coordinates
    """
    results = _model(image_bgr, conf=CONF_THRESH, verbose=False)

    boxes = []

    for r in results:
        if r.boxes is None:
            continue

        # xyxy are pixel coords relative to ORIGINAL image
        for box in r.boxes.xyxy.cpu().numpy():
            x1, y1, x2, y2 = box.astype(int)
            boxes.append((x1, y1, x2, y2))

    return boxes
