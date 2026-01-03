import cv2
from preprocess import preprocess_image
from tile_detection import detect_hand_tiles
from tile_recognition import extract_tile_images, classify_tile, normalize_tile

# 1️⃣ Read image
img_path = "backend/vision/tile_images/test1.jpg"
img = cv2.imread(img_path)
if img is None:
    raise ValueError(f"Image not found at {img_path}")

# Resize to detection scale
img_resized = cv2.resize(img, (800, 600))

# 2️⃣ Preprocess
processed = preprocess_image(img_resized, debug=False)

# 3️⃣ Detect tiles (TILTED BOXES)
tile_boxes = detect_hand_tiles(processed, debug=False)

# 4️⃣ Extract tile images using tilted boxes
tile_images = extract_tile_images(processed, tile_boxes)

# 5️⃣ Draw results
img_display = img_resized.copy()

for box, tile_img in zip(tile_boxes, tile_images):
    label = classify_tile(normalize_tile(tile_img))

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

cv2.imshow("Detected & Classified Tiles", img_display)
cv2.waitKey(0)
cv2.destroyAllWindows()

print(f"Detected {len(tile_images)} tiles")
