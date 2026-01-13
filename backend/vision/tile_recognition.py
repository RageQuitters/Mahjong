import cv2
import numpy as np

def extract_tile_images(rgb_img, tile_boxes, out_size=64):
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
        x, y, w, h = cv2.boundingRect(box)
        
        crop = rgb_img[y:y+h, x:x+w]

        if crop.size == 0:
            continue

        crop = cv2.resize(crop, (out_size, out_size))

        tiles.append(crop)

    return tiles
