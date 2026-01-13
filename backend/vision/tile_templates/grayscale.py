import cv2
import os
import numpy as np

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
IMG_PATH = "backend/vision/tile_templates/tile_misc.png"   # <-- your image
OUT_DIR = "tile_templates"
TILE_SIZE = (64, 64)

'''
# Manually tuned (based on this image)
ROWS = [
    # (y_start, y_end, tiles_in_row, row_prefix)
    (20, 120, 9, "DOT"),        # Circle suits
    (240, 360, 9, "CHAR"), # Character suits
    (480, 600, 9, "BAM"),     # Bamboo suits
]

# --------------------------------------------------
# Load image
# --------------------------------------------------
img = cv2.imread(IMG_PATH)
if img is None:
    raise ValueError("Image not found")

h, w, _ = img.shape

print("Image size:", h, w)
# add lines to visualise rows

for y in range(0, h, 20):
    cv2.line(img, (0, y), (w, y), (255, 0, 0), 1)
    cv2.putText(img, str(y), (10, y+15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,0,0), 1)

cv2.imshow("Row grid", img)
cv2.waitKey(0)


gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
os.makedirs(OUT_DIR, exist_ok=True)

# --------------------------------------------------
# Extract tiles
# --------------------------------------------------
tile_count = 0

for y1, y2, num_tiles, prefix in ROWS:
    row = gray[y1:y2, :]

    h, w = row.shape
    tile_w = w // num_tiles

    for i in range(num_tiles):
        x1 = int(i * tile_w)
        x2 = int((i + 1) * tile_w)

        tile = row[:, x1:x2]

        # Tight crop using threshold
        _, bw = cv2.threshold(tile, 200, 255, cv2.THRESH_BINARY_INV)
        coords = cv2.findNonZero(bw)

        if coords is None:
            continue

        x, y, w2, h2 = cv2.boundingRect(coords)
        tile = tile[y:y+h2, x:x+w2]

        # Normalize
        tile = cv2.resize(tile, TILE_SIZE, interpolation=cv2.INTER_AREA)
        _, tile = cv2.threshold(tile, 150, 255, cv2.THRESH_BINARY)

        fname = f"{i+1}_{prefix}.png"
        cv2.imwrite(os.path.join(OUT_DIR, fname), tile)

        tile_count += 1

print(f"Saved {tile_count} tile templates to {OUT_DIR}/")
'''

os.makedirs(OUT_DIR, exist_ok=True)

img = cv2.imread(IMG_PATH)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
H, W = gray.shape

print("Image size:", H, W)
# add lines to visualise rows

for y in range(0, H, 20):
    cv2.line(img, (0, y), (W, y), (255, 0, 0), 1)
    cv2.putText(img, str(y), (10, y+15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,0,0), 1)

cv2.imshow("Row grid", img)
cv2.waitKey(0)

def save_row(y1, y2, labels, subdir):
    row = gray[y1:y2, :]
    out_path = os.path.join(OUT_DIR, subdir)
    os.makedirs(out_path, exist_ok=True)
    
    # Calculate effective width
    row_width = row.shape[1]  # actual width of the row
    if labels == ["red", "green", "white"]:
        row_width = int(row_width * 3 / 4)  # only use left 3/4 of the row

    tile_w = row_width // len(labels)

    for i, label in enumerate(labels):
        x1 = i * tile_w
        x2 = x1 + tile_w
        tile = row[:, x1:x2]
        tile = cv2.resize(tile, TILE_SIZE, interpolation=cv2.INTER_AREA)
        _, tile = cv2.threshold(tile, 150, 255, cv2.THRESH_BINARY)

        cv2.imwrite(os.path.join(out_path, f"{label}.png"), tile)

# -------------------------------
# 1️⃣ Winds
# -------------------------------
save_row(
    y1=20,
    y2=160,
    labels=["east", "south", "west", "north"],
    subdir="winds"
)

# -------------------------------
# 2️⃣ Dragons
# -------------------------------
save_row(
    y1=280,
    y2=440,
    labels=["red", "green", "white"],
    subdir="dragons"
)

# -------------------------------
# 3️⃣ Flowers (top)
# -------------------------------
save_row(
    y1=560,
    y2=720,
    labels=["red_1", "red_2", "red_3", "red_4"],
    subdir="flowers"
)

# -------------------------------
# 4️⃣ Seasons (bottom)
# -------------------------------
save_row(
    y1=720,
    y2=840,
    labels=["blue_1", "blue_2", "blue_3", "blue_4"],
    subdir="seasons"
)

# -------------------------------
# 5️⃣ Animals
# -------------------------------
save_row(
    y1=840,
    y2=1000,
    labels=["cat", "rat", "chicken", "centipede"],
    subdir="animals"
)

print("✅ Special tile templates extracted")