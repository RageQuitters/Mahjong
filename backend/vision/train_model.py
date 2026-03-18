import os
import argparse
import torch
import torch.nn as nn
import torch.optim as optim

from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from model import TileCNN


# =============================================================================
# PATHS
# =============================================================================

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
SYNTH_ROOT = os.path.join(BASE_DIR, "tile_library", "synthetic")

# =============================================================================
# MODEL REGISTRY
#
# Maps (layer, type) → (dataset_subpath, save_name)
# =============================================================================

MODEL_REGISTRY = {
    # Layer 1
    ("1", "group"):      ("layer1",           "layer1_group.pth"),

    # Layer 2
    ("2", "suit_type"):  ("layer2/suit_type",  "layer2_suit_type.pth"),
    ("2", "honor_type"): ("layer2/honor_type",  "layer2_honor_type.pth"),
    ("2", "bonus_type"): ("layer2/bonus_type",  "layer2_bonus_type.pth"),

    # Layer 3
    ("3", "char"):       ("layer3/char",        "layer3_char.pth"),
    ("3", "bam"):        ("layer3/bam",          "layer3_bam.pth"),
    ("3", "dot"):        ("layer3/dot",          "layer3_dot.pth"),
    ("3", "wind"):       ("layer3/wind",         "layer3_wind.pth"),
    ("3", "dragon"):     ("layer3/dragon",       "layer3_dragon.pth"),

}


# =============================================================================
# TRAINING
# =============================================================================

def train(args):

    key = (args.layer, args.type)
    if key not in MODEL_REGISTRY:
        valid = "\n  ".join(f"--layer {l} --type {t}" for l, t in MODEL_REGISTRY)
        raise ValueError(
            f"Unknown combination --layer {args.layer} --type {args.type}.\n"
            f"Valid options:\n  {valid}"
        )

    data_subpath, save_name = MODEL_REGISTRY[key]
    DATA_ROOT  = os.path.join(SYNTH_ROOT, data_subpath)
    MODEL_PATH = os.path.join(MODELS_DIR, save_name)

    if not os.path.exists(DATA_ROOT):
        raise RuntimeError(f"Dataset path not found: {DATA_ROOT}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device : {device}")
    print(f"Layer        : {args.layer}")
    print(f"Type         : {args.type}")
    print(f"Dataset      : {DATA_ROOT}")
    print(f"Save path    : {MODEL_PATH}\n")

    # -------------------------------------------------------------------------
    # Transforms — augmentation done at dataset generation time
    # -------------------------------------------------------------------------

    transform = transforms.Compose([
        transforms.Resize((128, 128)),
        transforms.ToTensor(),
    ])

    # -------------------------------------------------------------------------
    # Datasets
    # -------------------------------------------------------------------------

    train_dataset = datasets.ImageFolder(os.path.join(DATA_ROOT, "train"), transform=transform)
    val_dataset   = datasets.ImageFolder(os.path.join(DATA_ROOT, "val"),   transform=transform)

    if len(train_dataset) == 0:
        raise RuntimeError("Train dataset is empty.")
    if len(val_dataset) == 0:
        raise RuntimeError("Val dataset is empty.")
    if train_dataset.classes != val_dataset.classes:
        raise RuntimeError(
            f"Class mismatch!\n  Train: {train_dataset.classes}\n  Val: {val_dataset.classes}"
        )

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True,  num_workers=0)
    val_loader   = DataLoader(val_dataset,   batch_size=args.batch_size, shuffle=False, num_workers=0)

    num_classes = len(train_dataset.classes)
    print(f"Classes ({num_classes}): {train_dataset.classes}")
    print(f"Train size   : {len(train_dataset)}")
    print(f"Val size     : {len(val_dataset)}\n")

    # -------------------------------------------------------------------------
    # Model
    # -------------------------------------------------------------------------

    model     = TileCNN(num_classes=num_classes).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)

    # -------------------------------------------------------------------------
    # Training loop
    # -------------------------------------------------------------------------

    best_val_acc  = 0.0
    best_epoch    = 0
    best_state    = None
    perfect_epoch = None   # epoch where 100% val acc was first reached

    for epoch in range(args.epochs):

        # Train
        model.train()
        running_loss = 0.0
        for imgs, labels in train_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            optimizer.zero_grad()
            loss = criterion(model(imgs), labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

        avg_loss = running_loss / len(train_loader)

        # Validate
        model.eval()
        correct = total = 0
        with torch.no_grad():
            for imgs, labels in val_loader:
                imgs, labels = imgs.to(device), labels.to(device)
                _, predicted = torch.max(model(imgs), 1)
                total   += labels.size(0)
                correct += (predicted == labels).sum().item()

        val_acc = 100.0 * correct / total
        marker  = ""

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_epoch   = epoch + 1
            best_state   = {
                "model_state": model.state_dict(),
                "classes":     train_dataset.classes,
                "num_classes": num_classes,
                "epoch":       epoch + 1,
                "val_acc":     val_acc,
                "layer":       args.layer,
                "type":        args.type,
            }
            marker = "  ← best"
            if val_acc == 100.0:
                perfect_epoch = epoch + 1

        print(f"Epoch [{epoch+1:>3}/{args.epochs}] Loss: {avg_loss:.4f}  Val Acc: {val_acc:.2f}%{marker}")

        # Early stopping — if 100% val acc was reached and 10 more epochs have passed
        if perfect_epoch is not None and (epoch + 1) >= perfect_epoch + 10:
            print(f"\nEarly stopping — 100% val acc reached at epoch {perfect_epoch}, ran 10 more epochs.")
            break

    # -------------------------------------------------------------------------
    # Save
    # -------------------------------------------------------------------------

    os.makedirs(MODELS_DIR, exist_ok=True)
    torch.save(best_state, MODEL_PATH)

    print(f"\nBest epoch   : {best_epoch}")
    print(f"Best val acc : {best_val_acc:.2f}%")
    print(f"Saved        : {MODEL_PATH}")


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Train a Mahjong tile classifier")

    parser.add_argument("--layer", required=True, choices=["1", "2", "3"],
                        help="Pipeline layer to train")
    parser.add_argument("--type",  required=True,
                        choices=["group", "suit_type", "honor_type", "bonus_type",
                                 "char", "bam", "dot", "wind", "dragon"],
                        help="Classifier type within the layer")
    parser.add_argument("--epochs",     type=int,   default=50)
    parser.add_argument("--batch_size", type=int,   default=32)
    parser.add_argument("--lr",         type=float, default=1e-3)

    args = parser.parse_args()
    train(args)
