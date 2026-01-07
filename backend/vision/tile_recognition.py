import cv2
import os
import numpy as np

TEMPLATE_SIZE = (64, 64)

# -------------------------------------------------
# Load tile templates
# -------------------------------------------------
def load_tile_templates(template_dir):
    """
    Loads all tile templates into memory.

    Returns:
        dict[label] = normalized template image
    """
    templates = {}

    for fname in os.listdir(template_dir):
        if not fname.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

        label = os.path.splitext(fname)[0]
        path = os.path.join(template_dir, fname)

        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue

        img = cv2.resize(img, TEMPLATE_SIZE, interpolation=cv2.INTER_AREA)
        _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

        templates[label] = img

    return templates


# -------------------------------------------------
# Extract tile image from tilted box
# -------------------------------------------------
def extract_tile_from_box(processed_img, box):
    """
    Extracts a tile using perspective warp from a tilted box.
    """
    box = np.array(box, dtype=np.float32)

    # Order points: tl, tr, br, bl
    rect = cv2.minAreaRect(box)
    pts = cv2.boxPoints(rect)

    w = int(rect[1][0])
    h = int(rect[1][1])

    if w <= 0 or h <= 0:
        return None

    dst = np.array([
        [0, 0],
        [w - 1, 0],
        [w - 1, h - 1],
        [0, h - 1]
    ], dtype=np.float32)

    M = cv2.getPerspectiveTransform(pts, dst)
    warped = cv2.warpPerspective(processed_img, M, (w, h))

    warped = cv2.resize(warped, TEMPLATE_SIZE, interpolation=cv2.INTER_AREA)
    _, warped = cv2.threshold(warped, 127, 255, cv2.THRESH_BINARY)

    return warped


# -------------------------------------------------
# Compare tile against templates
# -------------------------------------------------
def match_tile(tile_img, templates):
    """
    Returns best matching tile label.
    """
    best_label = "unknown"
    best_score = -1

    for label, template in templates.items():
        score = cv2.matchTemplate(
            tile_img,
            template,
            cv2.TM_CCOEFF_NORMED
        )[0][0]

        if score > best_score:
            best_score = score
            best_label = label

    return best_label, best_score


# -------------------------------------------------
# Full recognition pipeline
# -------------------------------------------------
def recognize_tiles(processed_img, tile_boxes, template_dir):
    """
    Recognizes each detected tile.

    Returns:
        list of dicts with box + label
    """
    templates = load_tile_templates(template_dir)

    results = []

    for box in tile_boxes:
        tile_img = extract_tile_from_box(processed_img, box)
        if tile_img is None:
            continue

        label, score = match_tile(tile_img, templates)

        results.append({
            "box": box,
            "label": label,
            "score": score,
            "tile_img": tile_img
        })

    return results