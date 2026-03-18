import os
import cv2
import shutil
import random
import numpy as np

# =============================================================================
# PATHS
# =============================================================================

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
RAW_ROOT   = os.path.join(BASE_DIR, "tile_library", "raw")
REAL_ROOT  = os.path.join(BASE_DIR, "tile_library", "real")
BG_ROOT    = os.path.join(BASE_DIR, "tile_library", "backgrounds")
SYNTH_ROOT = os.path.join(BASE_DIR, "tile_library", "synthetic")

# =============================================================================
# CONFIGURATION
# =============================================================================

TRAIN_SPLIT      = 0.7
IMG_SIZE         = 128

# Samples per tile for all classifiers EXCEPT layer1
SAMPLES_PER_TILE     = 500
VAL_SAMPLES_PER_TILE = 50

# Char gets more data — Chinese characters are visually similar and need more signal
CHAR_SAMPLES_PER_TILE     = 1500
CHAR_VAL_SAMPLES_PER_TILE = 100

# Dot gets more data + high grayscale — force dot counting instead of color shortcuts
DOT_SAMPLES_PER_TILE     = 1500
DOT_VAL_SAMPLES_PER_TILE = 100
DOT_GRAYSCALE_FRACTION   = 0.40

# Layer1 group classifier — balanced per group, not per tile
# suit=27 tiles, honor=7, bonus=8 → target 27*500=13500 per group
# so honor gets 13500/7 ≈ 1928 per tile, bonus gets 13500/8 ≈ 1687 per tile
LAYER1_SUIT_SAMPLES_PER_TILE  = 500
LAYER1_HONOR_SAMPLES_PER_TILE = 1929   # 7 tiles × 1929 ≈ 13503
LAYER1_BONUS_SAMPLES_PER_TILE = 1688   # 8 tiles × 1688 = 13504

# Layer1 val — balanced per group, targeting ~700 per group (≈2100 total)
# suit: 27 × 26 = 702, honor: 7 × 100 = 700, bonus: 8 × 88 = 704
LAYER1_SUIT_VAL_PER_TILE  = 26
LAYER1_HONOR_VAL_PER_TILE = 100
LAYER1_BONUS_VAL_PER_TILE = 88

# Train tier ratios — applied proportionally to whatever SAMPLES_PER_TILE is used
TIER_RATIOS = (0.50, 0.35, 0.15)   # minimal, moderate, aggressive

# Val tier distribution (fixed counts, must sum to VAL_SAMPLES_PER_TILE)
VAL_TIER_CLEAN    = 20
VAL_TIER_MODERATE = 20
VAL_TIER_COLOR    = 10

# Grayscale fractions
GRAYSCALE_FRACTION       = 0.80   # high grayscale — force shape learning across all classifiers
HONOR_GRAYSCALE_FRACTION = 0.80   # force shape learning for honor
# DOT_GRAYSCALE_FRACTION defined above with dot config

# Wind gets more data — 4 similar Chinese characters need more signal
WIND_SAMPLES_PER_TILE     = 1500
WIND_VAL_SAMPLES_PER_TILE = 100

# Real crop augmentation
REAL_SAMPLES_PER_IMAGE = 50    # augmented samples generated per real crop image
# REAL_ROOT tiles use same TIER_RATIOS but lighter augmentation

# Neighbour sliver
SLIVER_PROB      = 0.3
SLIVER_THICKNESS = 6

# =============================================================================
# DATASET STRUCTURE
#
#   synthetic/layer1/                    group: suit / honor / bonus
#   synthetic/layer2/suit_type/          char / bam / dot
#   synthetic/layer2/honor_type/         wind / dragon  (2-class split)
#   synthetic/layer2/bonus_type/         animal / flower
#   synthetic/layer3/char/               1-9
#   synthetic/layer3/bam/                1-9
#   synthetic/layer3/dot/                1-9
#   synthetic/layer3/wind/               EAST / SOUTH / WEST / NORTH
#   synthetic/layer3/dragon/             RED / GREEN / WHITE
#   (no layer3 for bonus — animal/flower classification stops at layer2)
# =============================================================================

# raw_category → (group, suit_type, honor_type, bonus_type)
# honor_type is "wind" or "dragon" — used for layer2 honor_type and layer3 routing
CATEGORY_MAP = {
    "bam":    ("suit",  "bam",  None,     None),
    "dot":    ("suit",  "dot",  None,     None),
    "char":   ("suit",  "char", None,     None),
    "dragon": ("honor", None,   "dragon", None),
    "wind":   ("honor", None,   "wind",   None),
    "flower": ("bonus", None,   None,     "flower"),
    "animal": ("bonus", None,   None,     "animal"),
}

# Layer1 samples per tile, keyed by group
LAYER1_SAMPLES = {
    "suit":  LAYER1_SUIT_SAMPLES_PER_TILE,
    "honor": LAYER1_HONOR_SAMPLES_PER_TILE,
    "bonus": LAYER1_BONUS_SAMPLES_PER_TILE,
}

# Layer1 val samples per tile, keyed by group
LAYER1_VAL = {
    "suit":  LAYER1_SUIT_VAL_PER_TILE,
    "honor": LAYER1_HONOR_VAL_PER_TILE,
    "bonus": LAYER1_BONUS_VAL_PER_TILE,
}

# =============================================================================
# BACKGROUND LOADING
# =============================================================================

def load_backgrounds():
    bgs = []
    if os.path.exists(BG_ROOT):
        for f in os.listdir(BG_ROOT):
            if f.lower().endswith((".jpg", ".jpeg", ".png")):
                img = cv2.imread(os.path.join(BG_ROOT, f))
                if img is not None:
                    bgs.append(img)
    if not bgs:
        bgs.append(np.full((IMG_SIZE, IMG_SIZE, 3), (34, 100, 34), dtype=np.uint8))
        print("Warning: No backgrounds found, using fallback green.")
    print(f"Loaded {len(bgs)} background image(s).")
    return bgs


def sample_background_patch(bgs, size):
    bg = random.choice(bgs)
    bh, bw = bg.shape[:2]
    if bh < size or bw < size:
        scale  = size / min(bh, bw) + 0.01
        bg     = cv2.resize(bg, (int(bw * scale), int(bh * scale)))
        bh, bw = bg.shape[:2]
    y = random.randint(0, bh - size)
    x = random.randint(0, bw - size)
    return bg[y:y+size, x:x+size].copy()

# =============================================================================
# COMPOSITING
# =============================================================================

def composite_tile(tile_img, bgs):
    canvas     = sample_background_patch(bgs, IMG_SIZE)
    max_jitter = int(IMG_SIZE * 0.05)
    dy = random.randint(-max_jitter, max_jitter)
    dx = random.randint(-max_jitter, max_jitter)

    ty = max(0, dy);   tx = max(0, dx)
    by = min(IMG_SIZE, IMG_SIZE + dy)
    bx = min(IMG_SIZE, IMG_SIZE + dx)
    sy = max(0, -dy);  sx = max(0, -dx)
    ey = sy + (by - ty); ex = sx + (bx - tx)

    canvas[ty:by, tx:bx] = tile_img[sy:ey, sx:ex]

    if random.random() < SLIVER_PROB:
        edge = random.choice(["top", "bottom", "left", "right"])
        c    = (230, 230, 230)
        if   edge == "top":    canvas[0:SLIVER_THICKNESS, :]           = c
        elif edge == "bottom": canvas[IMG_SIZE-SLIVER_THICKNESS:, :]   = c
        elif edge == "left":   canvas[:, 0:SLIVER_THICKNESS]           = c
        elif edge == "right":  canvas[:, IMG_SIZE-SLIVER_THICKNESS:]   = c

    return canvas

# =============================================================================
# AUGMENTATION PRIMITIVES
# =============================================================================

def resize(img):
    return cv2.resize(img, (IMG_SIZE, IMG_SIZE))


def rotate(img, max_angle):
    angle = random.uniform(-max_angle, max_angle)
    h, w  = img.shape[:2]
    M     = cv2.getRotationMatrix2D((w//2, h//2), angle, 1)
    return cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REPLICATE)


def perspective(img, strength):
    h, w  = img.shape[:2]
    shift = strength * min(w, h)
    pts1  = np.float32([[0,0],[w,0],[0,h],[w,h]])
    pts2  = np.float32([
        [random.uniform(0,shift),   random.uniform(0,shift)],
        [w-random.uniform(0,shift), random.uniform(0,shift)],
        [random.uniform(0,shift),   h-random.uniform(0,shift)],
        [w-random.uniform(0,shift), h-random.uniform(0,shift)],
    ])
    M = cv2.getPerspectiveTransform(pts1, pts2)
    return cv2.warpPerspective(img, M, (w, h), borderMode=cv2.BORDER_REPLICATE)


def brightness(img, low, high):
    factor = random.uniform(low, high)
    return np.clip(img.astype(np.float32) * factor, 0, 255).astype(np.uint8)


def noise(img, max_sigma):
    sigma = random.uniform(0, max_sigma)
    n     = np.random.normal(0, sigma, img.shape)
    return np.clip(img.astype(np.float32) + n, 0, 255).astype(np.uint8)


def color_jitter(img, strength=1.0):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:,:,0] = (hsv[:,:,0] + random.uniform(-15*strength, 15*strength)) % 180
    hsv[:,:,1] = np.clip(hsv[:,:,1] * random.uniform(1-0.4*strength, 1+0.4*strength), 0, 255)
    hsv[:,:,2] = np.clip(hsv[:,:,2] * random.uniform(1-0.3*strength, 1+0.3*strength), 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


def to_grayscale(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def scale_jitter(img):
    factor       = random.uniform(0.85, 1.15)
    h, w         = img.shape[:2]
    new_h, new_w = int(h * factor), int(w * factor)
    resized      = cv2.resize(img, (new_w, new_h))
    canvas       = np.zeros((IMG_SIZE, IMG_SIZE, 3), dtype=np.uint8)
    ch = min(new_h, IMG_SIZE); cw = min(new_w, IMG_SIZE)
    canvas[:ch, :cw] = resized[:ch, :cw]
    return canvas



def tile_tint(img):
    """Simulate real tile yellowing/cream tint under warm lighting."""
    tint  = np.array([[[random.uniform(-10, 5),    # B: slightly less
                         random.uniform(-5, 5),     # G: neutral
                         random.uniform(0, 20)]]])  # R: warmer
    return np.clip(img.astype(np.float32) + tint, 0, 255).astype(np.uint8)


def shadow_overlay(img):
    """Simulate a soft shadow cast across part of the tile."""
    h, w    = img.shape[:2]
    mask    = np.ones((h, w), dtype=np.float32)
    edge    = random.choice(["top", "bottom", "left", "right"])
    depth   = random.uniform(0.55, 0.85)   # how dark the shadow gets
    size    = random.randint(h // 4, h // 2)
    if   edge == "top":    mask[:size, :]  = np.linspace(depth, 1.0, size)[:, None]
    elif edge == "bottom": mask[-size:, :] = np.linspace(1.0, depth, size)[:, None]
    elif edge == "left":   mask[:, :size]  = np.linspace(depth, 1.0, size)[None, :]
    elif edge == "right":  mask[:, -size:] = np.linspace(1.0, depth, size)[None, :]
    mask = np.stack([mask, mask, mask], axis=2)
    return np.clip(img.astype(np.float32) * mask, 0, 255).astype(np.uint8)


def reflection_overlay(img):
    """Simulate a specular reflection/glare on the tile surface."""
    h, w   = img.shape[:2]
    canvas = img.astype(np.float32).copy()
    cx     = random.randint(w // 4, 3 * w // 4)
    cy     = random.randint(h // 4, 3 * h // 4)
    radius = random.randint(w // 6, w // 3)
    intensity = random.uniform(0.3, 0.7)
    Y, X   = np.ogrid[:h, :w]
    dist   = np.sqrt((X - cx)**2 + (Y - cy)**2)
    glow   = np.clip(1.0 - dist / radius, 0, 1) * intensity
    glow   = np.stack([glow, glow, glow], axis=2)
    canvas = np.clip(canvas + glow * 255, 0, 255)
    return canvas.astype(np.uint8)


def jpeg_compress(img, quality_low=50, quality_high=90):
    """Simulate JPEG compression artifacts."""
    quality = random.randint(quality_low, quality_high)
    _, enc  = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return cv2.imdecode(enc, cv2.IMREAD_COLOR)



# =============================================================================
# REAL CROP AUGMENTATION
# =============================================================================

def augment_real_minimal(img):
    """Light augmentation — preserve real-world features."""
    base  = random.choice([0, 90, 180, 270])
    angle = base + random.uniform(-15, 15)
    h, w  = img.shape[:2]
    M     = cv2.getRotationMatrix2D((w//2, h//2), angle, 1)
    img   = cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
    img   = brightness(img, low=0.90, high=1.10)
    return img


def augment_real_moderate(img):
    """Moderate augmentation — some variation while keeping real features."""
    base  = random.choice([0, 90, 180, 270])
    angle = base + random.uniform(-15, 15)
    h, w  = img.shape[:2]
    M     = cv2.getRotationMatrix2D((w//2, h//2), angle, 1)
    img   = cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
    img   = brightness(img, low=0.80, high=1.20)
    img   = jpeg_compress(img, quality_low=60, quality_high=95)
    return img


def augment_real_aggressive(img):
    """More variation — still no synthetic effects."""
    base  = random.choice([0, 90, 180, 270])
    angle = base + random.uniform(-15, 15)
    h, w  = img.shape[:2]
    M     = cv2.getRotationMatrix2D((w//2, h//2), angle, 1)
    img   = cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
    img   = brightness(img, low=0.70, high=1.30)
    img   = noise(img, max_sigma=5)
    img   = jpeg_compress(img, quality_low=40, quality_high=85)
    return img


def generate_real_sample(real_img, tier, grayscale_fraction):
    """Augment a real crop image."""
    img = resize(real_img)
    if tier == "minimal":
        img = augment_real_minimal(img)
    elif tier == "moderate":
        img = augment_real_moderate(img)
        if random.random() < grayscale_fraction:
            img = to_grayscale(img)
    elif tier == "aggressive":
        img = augment_real_aggressive(img)
        if random.random() < grayscale_fraction:
            img = to_grayscale(img)
    return img


def generate_real_for_classifier(
    classifier_root,
    class_label,
    tile_class,
    real_files,
    real_class_path,
    grayscale_fraction=GRAYSCALE_FRACTION,
    n_per_image=REAL_SAMPLES_PER_IMAGE,
):
    """
    Generate augmented samples from real crop images.
    n_per_image samples are generated per source image using TIER_RATIOS.
    Only generates train images — val remains synthetic only.
    """
    if not real_files:
        return

    n_total = len(real_files) * n_per_image
    tiers   = make_tier_list(n_total)

    for i, tier in enumerate(tiers):
        f        = real_files[i % len(real_files)]
        real_img = cv2.imread(os.path.join(real_class_path, f))
        if real_img is None:
            continue
        sample = generate_real_sample(real_img, tier, grayscale_fraction)
        name   = f"{tile_class}_real_{i:04d}.jpg"
        save(sample, os.path.join(classifier_root, "train", class_label, name))

# =============================================================================
# TIERED AUGMENTATION
# =============================================================================

def augment_minimal(img):
    img = rotate(img, max_angle=15)
    img = perspective(img, strength=0.03)
    img = brightness(img, low=0.90, high=1.10)
    return img


def augment_moderate(img):
    img = rotate(img, max_angle=90)
    img = perspective(img, strength=0.10)
    img = brightness(img, low=0.80, high=1.20)
    img = noise(img, max_sigma=5)
    img = color_jitter(img, strength=1.0)
    if random.random() < 0.5:
        img = tile_tint(img)
    if random.random() < 0.3:
        img = shadow_overlay(img)
    if random.random() < 0.5:
        img = jpeg_compress(img)
    return img


def augment_aggressive(img):
    img = rotate(img, max_angle=180)
    img = perspective(img, strength=0.20)
    img = brightness(img, low=0.65, high=1.35)
    img = noise(img, max_sigma=10)
    img = color_jitter(img, strength=1.0)
    img = scale_jitter(img)
    img = tile_tint(img)
    if random.random() < 0.5:
        img = shadow_overlay(img)
    if random.random() < 0.3:
        img = reflection_overlay(img)
    img = jpeg_compress(img, quality_low=40, quality_high=80)
    return img


def augment_val_moderate(img):
    base  = random.choice([0, 90, 180, 270])
    angle = base + random.uniform(-5, 5)
    h, w  = img.shape[:2]
    M     = cv2.getRotationMatrix2D((w//2, h//2), angle, 1)
    img   = cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
    img   = perspective(img, strength=0.08)
    return img

# =============================================================================
# SAMPLE GENERATORS
# =============================================================================

def generate_train_sample(raw_img, bgs, tier, grayscale_fraction):
    img = composite_tile(raw_img, bgs)
    if tier == "minimal":
        img = augment_minimal(img)
    elif tier == "moderate":
        img = augment_moderate(img)
        if random.random() < grayscale_fraction:
            img = to_grayscale(img)
    elif tier == "aggressive":
        img = augment_aggressive(img)
        if random.random() < grayscale_fraction:
            img = to_grayscale(img)
    return img


def generate_val_sample(raw_img, bgs, tier):
    img = composite_tile(raw_img, bgs)
    if tier == "moderate":
        img = augment_val_moderate(img)
    elif tier == "color":
        img = color_jitter(img, strength=0.5)
    return img

# =============================================================================
# SAVE HELPER
# =============================================================================

def save(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cv2.imwrite(path, img)

# =============================================================================
# PER-CLASSIFIER GENERATION
# =============================================================================

def make_tier_list(n_samples):
    """Build a shuffled tier list of length n_samples using TIER_RATIOS."""
    r_min, r_mod, r_agg = TIER_RATIOS
    n_min = round(n_samples * r_min)
    n_mod = round(n_samples * r_mod)
    n_agg = n_samples - n_min - n_mod   # absorb rounding remainder
    tiers = ["minimal"] * n_min + ["moderate"] * n_mod + ["aggressive"] * n_agg
    random.shuffle(tiers)
    return tiers


def generate_for_classifier(
    classifier_root,
    class_label,
    tile_class,
    train_files,
    val_files,
    tile_class_path,
    bgs,
    grayscale_fraction=GRAYSCALE_FRACTION,
    n_train=SAMPLES_PER_TILE,
    n_val=VAL_SAMPLES_PER_TILE,
):
    """
    Generate n_train train images and n_val val images for one tile
    into classifier_root/train/class_label/ and .../val/class_label/.

    class_label may differ from tile_class for layer1/layer2 classifiers
    where multiple tiles share the same class folder.
    """
    # --- TRAIN ---
    tiers = make_tier_list(n_train)

    for i, tier in enumerate(tiers):
        f       = train_files[i % len(train_files)]
        raw_img = cv2.imread(os.path.join(tile_class_path, f))
        if raw_img is None:
            continue
        raw_img = resize(raw_img)
        sample  = generate_train_sample(raw_img, bgs, tier, grayscale_fraction)
        name    = f"{tile_class}_{i:04d}.jpg"
        save(sample, os.path.join(classifier_root, "train", class_label, name))

    # --- VAL ---
    val_tiers = (
        ["clean"]    * VAL_TIER_CLEAN +
        ["moderate"] * VAL_TIER_MODERATE +
        ["color"]    * VAL_TIER_COLOR
    )
    random.shuffle(val_tiers)

    for i, tier in enumerate(val_tiers):
        f       = val_files[i % len(val_files)]
        raw_img = cv2.imread(os.path.join(tile_class_path, f))
        if raw_img is None:
            continue
        raw_img = resize(raw_img)
        sample  = generate_val_sample(raw_img, bgs, tier)
        name    = f"{tile_class}_val_{i:04d}.jpg"
        save(sample, os.path.join(classifier_root, "val", class_label, name))

# =============================================================================
# MAIN GENERATION
# =============================================================================

VALID_CLASSIFIERS = ["layer1", "suit_type", "honor_type", "bonus_type", "char", "bam", "dot", "wind", "dragon"]


def generate(only=None):
    """
    Generate synthetic dataset.

    Args:
        only (list[str] | None): if provided, only regenerate these classifiers
                                 and leave all others untouched.
                                 Valid values: layer1, suit_type, honor_type, bonus_type,
                                               char, bam, dot, wind, dragon
    """
    if only is not None:
        invalid = [k for k in only if k not in VALID_CLASSIFIERS]
        if invalid:
            raise ValueError(f"Unknown classifier(s): {invalid}. Valid: {VALID_CLASSIFIERS}")

    paths = {
        "layer1":     os.path.join(SYNTH_ROOT, "layer1"),
        "suit_type":  os.path.join(SYNTH_ROOT, "layer2", "suit_type"),
        "honor_type": os.path.join(SYNTH_ROOT, "layer2", "honor_type"),
        "bonus_type": os.path.join(SYNTH_ROOT, "layer2", "bonus_type"),
        "char":       os.path.join(SYNTH_ROOT, "layer3", "char"),
        "bam":        os.path.join(SYNTH_ROOT, "layer3", "bam"),
        "dot":        os.path.join(SYNTH_ROOT, "layer3", "dot"),
        "wind":       os.path.join(SYNTH_ROOT, "layer3", "wind"),
        "dragon":     os.path.join(SYNTH_ROOT, "layer3", "dragon"),
    }

    if only is None:
        # Full rebuild — wipe everything
        if os.path.exists(SYNTH_ROOT):
            shutil.rmtree(SYNTH_ROOT)
        os.makedirs(SYNTH_ROOT)
        targets = set(VALID_CLASSIFIERS)
        print("\nGenerating full dataset...\n")
    else:
        # Partial rebuild — only wipe the requested classifier folders
        os.makedirs(SYNTH_ROOT, exist_ok=True)
        targets = set(only)
        for key in targets:
            path = paths[key]
            if os.path.exists(path):
                shutil.rmtree(path)
        print(f"\nRegenerating: {sorted(targets)}\n")

    bgs = load_backgrounds()

    print("\nGenerating dataset...\n")

    for raw_category in sorted(os.listdir(RAW_ROOT)):
        if raw_category not in CATEGORY_MAP:
            continue

        group, suit_type, honor_class, bonus_type = CATEGORY_MAP[raw_category]
        raw_category_path = os.path.join(RAW_ROOT, raw_category)

        for tile_class in sorted(os.listdir(raw_category_path)):
            tile_class_path = os.path.join(raw_category_path, tile_class)
            if not os.path.isdir(tile_class_path):
                continue

            files = [
                f for f in os.listdir(tile_class_path)
                if f.lower().endswith((".jpg", ".jpeg", ".png"))
            ]
            if not files:
                print(f"  Warning: no images for {tile_class}, skipping.")
                continue

            random.shuffle(files)
            split       = max(1, int(len(files) * TRAIN_SPLIT))
            train_files = files[:split]
            val_files   = files[split:] if len(files) > 1 else files

            def gen(classifier_key, class_label,
                    gs=GRAYSCALE_FRACTION,
                    n_train=SAMPLES_PER_TILE,
                    n_val=VAL_SAMPLES_PER_TILE):
                if classifier_key not in targets:
                    return
                generate_for_classifier(
                    paths[classifier_key], class_label,
                    tile_class, train_files, val_files,
                    tile_class_path, bgs,
                    grayscale_fraction=gs,
                    n_train=n_train,
                    n_val=n_val,
                )

            # ------------------------------------------------------------------
            # Layer 1 — balanced per group
            # ------------------------------------------------------------------
            l1_n = LAYER1_SAMPLES[group]
            l1_v = LAYER1_VAL[group]
            gen("layer1", group, n_train=l1_n, n_val=l1_v)

            # ------------------------------------------------------------------
            # Layer 2
            # ------------------------------------------------------------------
            if suit_type is not None:
                gen("suit_type", suit_type)
            if honor_class is not None:
                gen("honor_type", honor_class, gs=HONOR_GRAYSCALE_FRACTION)
            if bonus_type is not None:
                gen("bonus_type", bonus_type)

            # ------------------------------------------------------------------
            # Layer 3
            # ------------------------------------------------------------------
            if suit_type == "char":
                gen("char", tile_class, n_train=CHAR_SAMPLES_PER_TILE, n_val=CHAR_VAL_SAMPLES_PER_TILE)
            elif suit_type == "bam":
                gen("bam", tile_class)
            elif suit_type == "dot":
                gen("dot", tile_class, gs=DOT_GRAYSCALE_FRACTION, n_train=DOT_SAMPLES_PER_TILE, n_val=DOT_VAL_SAMPLES_PER_TILE)

            if honor_class == "wind":
                gen("wind", tile_class, gs=HONOR_GRAYSCALE_FRACTION, n_train=WIND_SAMPLES_PER_TILE, n_val=WIND_VAL_SAMPLES_PER_TILE)
            elif honor_class == "dragon":
                gen("dragon", tile_class, gs=HONOR_GRAYSCALE_FRACTION)

            print(f"  [{group}] {tile_class}: L1={l1_n} train | {l1_v} val (L1) | others={SAMPLES_PER_TILE} train | {VAL_SAMPLES_PER_TILE} val")

    # ------------------------------------------------------------------
    # Pass 2 — Real crops from tile_library/real/
    # ------------------------------------------------------------------
    print("\nAdding real crops...\n")

    # Maps real/ folder structure to (classifier_key, class_label, grayscale)
    # Each entry: (category, tile_class) -> list of (classifier_key, class_label, gs, n_per_image)
    def get_real_entries(category, tile_class):
        """Return list of (classifier_key, class_label, gs) for a real crop tile."""
        entries = []
        info = CATEGORY_MAP.get(category)
        if info is None:
            return entries
        group, suit_type, honor_class, bonus_type = info

        # Layer 1
        l1_n = LAYER1_SAMPLES[group]
        # For layer1 real crops, scale proportionally: real adds 500 per tile equiv
        # Use fixed 50/image regardless of group — layer1 balance handled by synthetic
        entries.append(("layer1", group, GRAYSCALE_FRACTION))

        # Layer 2
        if suit_type is not None:
            entries.append(("suit_type", suit_type, GRAYSCALE_FRACTION))
        if honor_class is not None:
            entries.append(("honor_type", honor_class, HONOR_GRAYSCALE_FRACTION))
        if bonus_type is not None:
            entries.append(("bonus_type", bonus_type, GRAYSCALE_FRACTION))

        # Layer 3
        if suit_type == "char":
            entries.append(("char", tile_class, GRAYSCALE_FRACTION))
        elif suit_type == "bam":
            entries.append(("bam", tile_class, GRAYSCALE_FRACTION))
        elif suit_type == "dot":
            entries.append(("dot", tile_class, DOT_GRAYSCALE_FRACTION))
        if honor_class == "wind":
            entries.append(("wind", tile_class, HONOR_GRAYSCALE_FRACTION))
        elif honor_class == "dragon":
            entries.append(("dragon", tile_class, HONOR_GRAYSCALE_FRACTION))

        return entries

    if os.path.exists(REAL_ROOT):
        for category in sorted(os.listdir(REAL_ROOT)):
            real_category_path = os.path.join(REAL_ROOT, category)
            if not os.path.isdir(real_category_path):
                continue

            for tile_class in sorted(os.listdir(real_category_path)):
                real_class_path = os.path.join(real_category_path, tile_class)
                if not os.path.isdir(real_class_path):
                    continue

                real_files = [
                    f for f in os.listdir(real_class_path)
                    if f.lower().endswith((".jpg", ".jpeg", ".png"))
                ]
                if not real_files:
                    continue

                entries = get_real_entries(category, tile_class)
                for classifier_key, class_label, gs in entries:
                    if classifier_key not in targets:
                        continue
                    generate_real_for_classifier(
                        paths[classifier_key], class_label,
                        tile_class, real_files, real_class_path,
                        grayscale_fraction=gs,
                    )

                n_real = len(real_files) * REAL_SAMPLES_PER_IMAGE
                print(f"  [{category}] {tile_class}: {len(real_files)} real images → {n_real} samples")
    else:
        print("  No real crops found, skipping.")

    print("\nDataset generation complete.")
    print("\nExpected layer1 sizes (balanced):")
    print(f"  train - suit: {27*LAYER1_SUIT_SAMPLES_PER_TILE}, honor: {7*LAYER1_HONOR_SAMPLES_PER_TILE}, bonus: {8*LAYER1_BONUS_SAMPLES_PER_TILE}")
    print(f"  val   - suit: {27*LAYER1_SUIT_VAL_PER_TILE}, honor: {7*LAYER1_HONOR_VAL_PER_TILE}, bonus: {8*LAYER1_BONUS_VAL_PER_TILE}")
    print("\nOutput structure:")
    for key, path in paths.items():
        print(f"  {path.replace(BASE_DIR, '.')}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate synthetic Mahjong tile dataset")
    parser.add_argument(
        "--only", nargs="+", metavar="CLASSIFIER",
        help=f"Regenerate only specific classifiers. Choices: {VALID_CLASSIFIERS}"
    )
    args = parser.parse_args()
    generate(only=args.only)
