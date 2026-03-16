import os
import random
import shutil

IMAGE_DIR = "images"
LABEL_DIR = "labels"

OUT_IMG_TRAIN = "images/train"
OUT_IMG_VAL   = "images/val"
OUT_LAB_TRAIN = "labels/train"
OUT_LAB_VAL   = "labels/val"

os.makedirs(OUT_IMG_TRAIN, exist_ok=True)
os.makedirs(OUT_IMG_VAL, exist_ok=True)
os.makedirs(OUT_LAB_TRAIN, exist_ok=True)
os.makedirs(OUT_LAB_VAL, exist_ok=True)

images = [f for f in os.listdir(IMAGE_DIR) if f.endswith(".jpg")]
random.shuffle(images)

split = int(0.8 * len(images))
train_imgs = images[:split]
val_imgs = images[split:]

def copy_pair(img_name, img_dst, lab_dst):
    shutil.copy(
        os.path.join(IMAGE_DIR, img_name),
        os.path.join(img_dst, img_name)
    )
    label_name = img_name.replace(".jpg", ".txt")
    shutil.copy(
        os.path.join(LABEL_DIR, label_name),
        os.path.join(lab_dst, label_name)
    )

for img in train_imgs:
    copy_pair(img, OUT_IMG_TRAIN, OUT_LAB_TRAIN)

for img in val_imgs:
    copy_pair(img, OUT_IMG_VAL, OUT_LAB_VAL)

print(f"Train images: {len(train_imgs)}")
print(f"Val images:   {len(val_imgs)}")
