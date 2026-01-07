import cv2
from preprocess import preprocess_image
from tile_detection import detect_hand_tiles
from tile_recognition import recognize_tiles

# ---------------------------------------
# Main detection + recognition pipeline
# ---------------------------------------

# 1️⃣ Load image
img_path = "backend/vision/tile_images/test1.jpg"
template_dir = "tile_templates"  # folder of labeled tile images

img = cv2.imread(img_path)
if img is None:
    raise ValueError(f"Image not found at {img_path}")

# Resize to detection scale (MUST match detection assumptions)
img_resized = cv2.resize(img, (800, 600))

# 2️⃣ Preprocess image
processed = preprocess_image(img_resized, debug=False)

# Optional debug
cv2.imshow("Processed", processed)
cv2.waitKey(0)

# 3️⃣ Detect tiles (returns TILTED BOXES)
tile_boxes = detect_hand_tiles(processed, debug=True)

print(f"Detected {len(tile_boxes)} tile candidates")

# 4️⃣ Recognize tiles using template matching
results = recognize_tiles(
    processed_img=processed,
    tile_boxes=tile_boxes,
    template_dir=template_dir
)

# 5️⃣ Draw results
img_display = img_resized.copy()

for res in results:
    box = res["box"]
    label = res["label"]
    score = res["score"]

    # Draw tilted box
    cv2.polylines(
        img_display,
        [box],
        isClosed=True,
        color=(0, 0, 255),
        thickness=2
    )

    # Label near top-left of box
    x, y = box[0]
    cv2.putText(
        img_display,
        f"{label} ({score:.2f})",
        (int(x), int(y) - 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 255, 0),
        1
    )
    print(label, score)

# 6️⃣ Show final output
cv2.imshow("Detected & Recognized Tiles", img_display)
cv2.waitKey(0)
cv2.destroyAllWindows()