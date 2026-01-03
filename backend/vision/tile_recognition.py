import cv2
import numpy as np

def extract_tile_images(processed_img, tile_boxes):
    """
    Extract tile images using tilted boxes.

    Args:
        processed_img: binary image
        tile_boxes: list of (4,2) tilted box arrays

    Returns:
        list of cropped tile images
    """
    tiles = []

    for box in tile_boxes:
        box = box.astype(np.int32)

        # Create mask for the rotated rectangle
        mask = np.zeros(processed_img.shape, dtype=np.uint8)
        cv2.fillPoly(mask, [box], 255)

        # Apply mask
        masked = cv2.bitwise_and(processed_img, processed_img, mask=mask)

        # Crop bounding rectangle
        x, y, w, h = cv2.boundingRect(box)
        tile = masked[y:y+h, x:x+w]

        if tile.size > 0:
            tiles.append(tile)

    return tiles


def normalize_tile(tile_img, size=(64, 64)):
    return cv2.resize(tile_img, size, interpolation=cv2.INTER_AREA)


def simple_tile_features(tile):
    white_pixels = cv2.countNonZero(tile)
    h, w = tile.shape
    density = white_pixels / (h * w + 1e-6)

    vertical_proj = tile.sum(axis=0)
    horizontal_proj = tile.sum(axis=1)

    return {
        "density": density,
        "v_peaks": (vertical_proj > vertical_proj.mean()).sum(),
        "h_peaks": (horizontal_proj > horizontal_proj.mean()).sum()
    }


def classify_tile(tile):
    features = simple_tile_features(tile)

    if features["density"] < 0.08:
        return "unknown"

    if features["v_peaks"] > features["h_peaks"] * 2:
        return "bamboo"

    if features["density"] > 0.35:
        return "dots"

    return "characters"
