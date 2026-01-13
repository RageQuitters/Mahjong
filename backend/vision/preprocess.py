import cv2
import numpy as np

def preprocess_image(img, resize_dim=(800, 600), debug=False):
    img_resized = cv2.resize(img, resize_dim)
    H, W = img_resized.shape[:2]
    
    gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
    blur = cv2.bilateralFilter(gray, 7, 50, 50)
    edges = cv2.Canny(blur, 40, 120)

    # --- CLEAR TABLE EDGE ---
    chip_zone_y = int(H * 0.90) 
    edges[chip_zone_y:, :] = 0 

    # --- CRITICAL CHANGE: VERTICAL ONLY DILATION ---
    # Use (15, 1) kernel: effectively makes vertical lines longer 
    # but does NOT merge items side-by-side.    
    kernel = np.ones((15, 1), np.uint8) 
    dilated = cv2.dilate(edges, kernel, iterations=2)

    # Filter noise
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(dilated, connectivity=8)
    clean_mask = np.zeros_like(edges)

    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        # Keep decent sized blobs
        if area > 20: 
            clean_mask[labels == i] = 255

    cleaned_edges = cv2.bitwise_and(edges, clean_mask)

    if debug:
        cv2.imshow("Debug: Vertical Enhanced", dilated)
        cv2.waitKey(0)

    return cleaned_edges
