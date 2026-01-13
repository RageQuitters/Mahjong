import cv2
from preprocess import preprocess_image
from tile_detection import detect_hand_tiles
from tile_recognition import extract_tile_images
from inference import classify_tile_image

#img_path = "backend/vision/tile_images/test1.jpg"

def run_tile_detection(img_path):
    img = cv2.imread(img_path)
    if img is None:
        raise ValueError(f"Image not found: {img_path}")

    img_resized = cv2.resize(img, (800, 600))

    # --- Step 1: preprocess for detection ---
    processed = preprocess_image(img_resized)

    # --- Step 2: detect tiles ---
    tile_boxes = detect_hand_tiles(processed)

    # --- Step 3: extract RGB crops for CNN ---
    tile_images = extract_tile_images(img_resized, tile_boxes)

    # --- Step 4: classify each tile ---
    img_display = img_resized.copy()

    detected_tiles = []
    
    for box, tile_img in zip(tile_boxes, tile_images):
        label = classify_tile_image(tile_img)  # CNN output
        detected_tiles.append(label)

        # Draw tilted box
        cv2.polylines(img_display, [box], True, (0, 0, 255), 2)

        # Label near top-left corner of box
        x, y = box[0]
        cv2.putText(
            img_display,
            label,
            (int(x), int(y) - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1
        )

    print("Detected tiles:")
    for t in detected_tiles:
        print(t)

    cv2.imshow("Detected & Classified Tiles", img_display)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    print(f"Detected {len(tile_images)} tiles")



# test script
img_path = "tile_images/test8.jpg"
run_tile_detection(img_path)
    
