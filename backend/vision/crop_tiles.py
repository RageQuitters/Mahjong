def crop_tiles(image_bgr, boxes, padding=4):
    """
    Args:
        image_bgr (np.ndarray): full-resolution BGR image
        boxes (List[tuple]): [(x1, y1, x2, y2)]
        padding (int): optional padding in pixels

    Returns:
        List[np.ndarray]: cropped BGR tile images
    """
    h, w, _ = image_bgr.shape
    crops = []

    for (x1, y1, x2, y2) in boxes:
        x1 = max(0, x1 - padding)
        y1 = max(0, y1 - padding)
        x2 = min(w, x2 + padding)
        y2 = min(h, y2 + padding)

        crop = image_bgr[y1:y2, x1:x2]
        if crop.size > 0:
            crops.append(crop)

    return crops
