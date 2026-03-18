import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
from vision.classify import classify_image



IMAGE_PATH = "tile_images/test8.jpg"
DISPLAY_MAX_WIDTH = 1200  # for screen only
DISPLAY_MAX_HEIGHT = 800

def resize_for_display(image):
    h, w = image.shape[:2]

    scale_w = DISPLAY_MAX_WIDTH / w
    scale_h = DISPLAY_MAX_HEIGHT / h
    scale = min(1.0, scale_w, scale_h)  # never upscale

    if scale == 1.0:
        return image

    new_size = (int(w * scale), int(h * scale))
    return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)

def main():
    image_bgr = cv2.imread(IMAGE_PATH)
    if image_bgr is None:
        raise FileNotFoundError(IMAGE_PATH)

    results = classify_image(image_bgr)

    # Print clean results
    print("Detections:")
    for i, r in enumerate(results):
        print(f"{i+1}. Box={r['box']} → {r['class_name']}")

    # Draw on a COPY
    vis = image_bgr.copy()
    for r in results:
        x1, y1, x2, y2 = r["box"]
        label = r["class_name"]

        cv2.rectangle(vis, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(
            vis,
            label,
            (x1, max(0, y1 - 6)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

    vis = resize_for_display(vis)
    cv2.imshow("Tile Classification", vis)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
