import os
import random
import cv2
import numpy as np
from pathlib import Path

from typing import Tuple
from PIL import Image, ImageEnhance, ImageFilter

import torch
from torch.utils.data import Dataset
from torchvision.transforms import functional as F
import torchvision.transforms as T

class MahjongTileDataset(Dataset):
    def __init__(self, root_dir: str, image_size: int = 128):

        self.root_dir = root_dir
        self.image_size = image_size

        self.samples = []
        self.class_to_idx = {}

        classes = sorted(os.listdir(root_dir))
        for idx, cls in enumerate(classes):
            cls_path = os.path.join(root_dir, cls)
            if not os.path.isdir(cls_path):
                continue

            self.class_to_idx[cls] = idx
            for fname in os.listdir(cls_path):
                if fname.lower().endswith((".png", ".jpg", ".jpeg")):
                    self.samples.append(
                        (os.path.join(cls_path, fname), idx)
                    )

        if len(self.samples) == 0:
            raise RuntimeError(f"No images found in {root_dir}")

        self.transform = T.Compose([
            T.Resize((self.image_size, self.image_size)),
            T.ToTensor(),
            T.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        ])
        
    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        img_path, label = self.samples[idx]
        image = Image.open(img_path).convert("RGB")

        if self.transform:
            image = self.transform(image)

        return image, label

# -----------------------------
# Augmentation utilities
# -----------------------------

def random_blur(image: Image.Image, p: float = 0.3, max_radius: float = 2.0) -> Image.Image:
    if random.random() < p:
        radius = random.uniform(0.5, max_radius)
        image = image.filter(ImageFilter.GaussianBlur(radius))
    return image

def random_color_jitter(
    image: Image.Image,
    p: float = 0.2,
    brightness=0.3,
    contrast=0.3,
    saturation=0.3,
    hue=0.03,
) -> Image.Image:
    if random.random() < p:
        jitter = T.ColorJitter(
            brightness=brightness,
            contrast=contrast,
            saturation=saturation,
            hue=hue,
        )
        image = jitter(image)
    return image

def random_perspective(
    img: Image.Image,
    p: float = 0.8,
    distortion_scale: float = 0.35
) -> Image.Image:
    """
    Apply a random perspective transform to a PIL image.

    p: probability of applying the transform
    distortion_scale: how strong the perspective distortion is
    """

    if random.random() > p:
        return img

    w, h = img.size

    dx = distortion_scale * w
    dy = distortion_scale * h

    startpoints = [
        (0, 0),
        (w, 0),
        (w, h),
        (0, h),
    ]

    endpoints = [
        (random.uniform(0, dx), random.uniform(0, dy)),
        (random.uniform(w - dx, w), random.uniform(0, dy)),
        (random.uniform(w - dx, w), random.uniform(h - dy, h)),
        (random.uniform(0, dx), random.uniform(h - dy, h)),
    ]

    return F.perspective(
        img,
        startpoints=startpoints,
        endpoints=endpoints,
        interpolation=F.InterpolationMode.BILINEAR,
        fill=0
    )

# -----------------------------
# Dataset generation
# -----------------------------

def generate_synthetic_dataset(
    tile_library_dir: str,
    output_dir: str,
    images_per_class: int = 500,
    image_size: int = 128
):


    train_ratio = 0.9

    for split in ["train", "val"]:
        os.makedirs(os.path.join(output_dir, split), exist_ok=True)

    classes = sorted(os.listdir(tile_library_dir))

    for cls in classes:
        cls_src = os.path.join(tile_library_dir, cls)
        if not os.path.isdir(cls_src):
            continue

        base_images = [
            Image.open(os.path.join(cls_src, f)).convert("RGB")
            for f in os.listdir(cls_src)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        ]

        if len(base_images) == 0:
            continue

        for split in ["train", "val"]:
            os.makedirs(os.path.join(output_dir, split, cls), exist_ok=True)

        for i in range(images_per_class):
            img = random.choice(base_images).copy()

            # ------------------ GEOMETRIC AUGMENTATIONS ------------------
            # Rotation (keep but slightly more realistic)
            angle = random.uniform(0, 360)
            img = F.rotate(img, angle, expand=True)

            # Perspective (still useful, but not always)
            if random.random() < 0.7:
                img = random_perspective(img)

            # ------------------ PHOTOMETRIC AUGMENTATIONS ------------------
            img = random_blur(img)          # p = 0.3
            img = random_color_jitter(img)  # p = 0.2

            # Final resize
            img = img.resize((image_size, image_size))

            # Train / val split
            split = "train" if random.random() < train_ratio else "val"
            out_path = os.path.join(output_dir, split, cls, f"{i:04d}.png")
            img.save(out_path)
            
        print(f"[✓] Generated {images_per_class} images for {cls}")

# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    generate_synthetic_dataset(
        tile_library_dir="tile_library",
        output_dir="dataset"
    )
