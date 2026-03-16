from vision.detect_tiles import detect_tiles
from vision.crop_tiles import crop_tiles
from vision.inference import classify_tile_image

def classify_image(image_bgr):
    """
    Full pipeline:
      image → boxes → crops → predictions

    Returns:
        List[dict]:
        [
          {
            "box":        (x1, y1, x2, y2),
            "class_name": "3_BAM" | "SOUTH" | "RAT" | "2_FLOWER" | ...
          },
          ...
        ]
    """
    boxes = detect_tiles(image_bgr)
    crops = crop_tiles(image_bgr, boxes)

    results = []
    for i, (box, crop) in enumerate(zip(boxes, crops)):
        class_name = classify_tile_image(crop, tile_id=f"tile_{i:03d}")
        results.append({
            "box":        box,
            "class_name": class_name,
        })

    return results
