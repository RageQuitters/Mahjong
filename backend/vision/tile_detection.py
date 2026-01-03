import numpy as np
import cv2

def detect_hand_tiles(cleaned_edges, debug=False):
    H, W = cleaned_edges.shape
    
    # ROI focused only on the player's concealed hand (Bottom 35%)
    roi_y1, roi_y2 = int(H * 0.65), int(H * 0.98) 
    roi_x1, roi_x2 = int(W * 0.02), int(W * 0.98) 
    hand_roi = cleaned_edges[roi_y1:roi_y2, roi_x1:roi_x2]

    # Vertical Projection
    projection = np.sum(hand_roi, axis=0)
    if np.sum(projection) == 0: return []

    # Smoothing (higher number = less accidental slicing)
    smooth_signal = np.convolve(projection, np.ones(15)/15, mode='same')
    
    # Adaptive Threshold
    thresh = np.mean(smooth_signal) * 0.35 
    is_active = smooth_signal > thresh

    tile_boxes = []
    start_x = None
    
    # Calibration for 800px width
    EST_WIDTH = 50 

    for i, active in enumerate(is_active):
        if active and start_x is None:
            start_x = i
        elif not active and start_x is not None:
            width = i - start_x
            
            # Case A: Single Tile (Upper bound 80px to avoid slicing)
            if 20 < width < 80:
                box_pts = get_tilted_box(hand_roi, start_x, i, roi_x1, roi_y1)
                if box_pts is not None: tile_boxes.append(box_pts)
            
            # Case B: Touching Tiles (Split them)
            elif width >= 80:
                num_tiles = int(round(width / EST_WIDTH))
                num_tiles = max(1, num_tiles)
                
                sub_width = width / num_tiles 
                for k in range(num_tiles):
                    s = int(start_x + (k * sub_width))
                    e = int(start_x + ((k+1) * sub_width))
                    box_pts = get_tilted_box(hand_roi, s, e, roi_x1, roi_y1)
                    if box_pts is not None: tile_boxes.append(box_pts)

            start_x = None

    return tile_boxes

def get_tilted_box(roi_img, x_start, x_end, offset_x, offset_y):
    # Slice the tile region
    tile_slice = roi_img[:, x_start:x_end]
    coords = np.column_stack(np.where(tile_slice > 0))
    
    if len(coords) > 5: # Need enough points to form a rectangle
        # minAreaRect finds the best tilted fit
        # coords is (y, x), we swap to (x, y) for OpenCV
        rect = cv2.minAreaRect(coords[:, ::-1])
        box = cv2.boxPoints(rect)
        
        # Offset back to original image space
        box[:, 0] += x_start + offset_x
        box[:, 1] += offset_y
        
        return box.astype(np.int32)
    return None