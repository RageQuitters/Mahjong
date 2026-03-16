import os
import argparse
import torch
import numpy as np

from torchvision import datasets, transforms
from torch.utils.data import DataLoader

from model import TileCNN

# =============================================================================
# PATHS
# =============================================================================

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
SYNTH_ROOT = os.path.join(BASE_DIR, "tile_library", "synthetic")

MODEL_REGISTRY = {
    ("1", "group"):       ("layer1",              "layer1_group.pth"),
    ("2", "suit_type"):   ("layer2/suit_type",    "layer2_suit_type.pth"),
    ("2", "honor_type"):  ("layer2/honor_type",   "layer2_honor_type.pth"),
    ("2", "bonus_type"):  ("layer2/bonus_type",   "layer2_bonus_type.pth"),
    ("3", "char"):        ("layer3/char",          "layer3_char.pth"),
    ("3", "bam"):         ("layer3/bam",           "layer3_bam.pth"),
    ("3", "dot"):         ("layer3/dot",           "layer3_dot.pth"),
    ("3", "wind"):        ("layer3/wind",          "layer3_wind.pth"),
    ("3", "dragon"):      ("layer3/dragon",        "layer3_dragon.pth"),
}

# =============================================================================
# DISPLAY HELPERS
# =============================================================================

def print_per_class_accuracy(matrix, classes):
    print("Per-class accuracy (worst → best):\n")
    results = []
    for i, cls in enumerate(classes):
        total   = matrix[i].sum()
        correct = matrix[i, i]
        acc     = 100.0 * correct / total if total > 0 else 0.0
        results.append((acc, cls, correct, total))
    results.sort()
    for acc, cls, correct, total in results:
        bar = "█" * int(acc/2) + "░" * (50 - int(acc/2))
        print(f"  {cls:<20} {bar}  {acc:5.1f}%  ({correct}/{total})")
    print()


def print_top_confusions(matrix, classes, top_n=10):
    pairs = []
    n = len(classes)
    for i in range(n):
        for j in range(n):
            if i != j and matrix[i, j] > 0:
                pairs.append((matrix[i, j], classes[i], classes[j]))
    pairs.sort(reverse=True)
    print(f"Top {top_n} confusions (true → predicted):\n")
    for count, true_cls, pred_cls in pairs[:top_n]:
        print(f"  {true_cls:<20} → {pred_cls:<20}  ({count} times)")
    print()


def print_confusion_matrix(matrix, classes, max_class_len=12):
    n     = len(classes)
    col_w = max(6, max_class_len)
    labels = [c[:col_w] for c in classes]
    row_w  = col_w + 2
    header = " " * row_w + "  ".join(f"{l:>{col_w}}" for l in labels)
    print("\nConfusion Matrix (rows=true, cols=predicted):\n")
    print(header)
    print("-" * len(header))
    for i, row_label in enumerate(labels):
        total = matrix[i].sum()
        cells = []
        for j, val in enumerate(matrix[i]):
            cell = f"[{val:>{col_w-2}}]" if i == j else f"{val:>{col_w}}"
            cells.append(cell)
        pct = 100.0 * matrix[i, i] / total if total > 0 else 0.0
        print(f"{row_label:>{row_w}}  {'  '.join(cells)}   ({pct:.1f}%)")
    print()

# =============================================================================
# EVALUATE
# =============================================================================

def evaluate(args):
    key = (args.layer, args.type)
    if key not in MODEL_REGISTRY:
        raise ValueError(f"Unknown --layer {args.layer} --type {args.type}")

    data_subpath, model_file = MODEL_REGISTRY[key]
    DATA_ROOT  = os.path.join(SYNTH_ROOT, data_subpath)
    MODEL_PATH = os.path.join(MODELS_DIR, model_file)

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}")
    if not os.path.exists(DATA_ROOT):
        raise RuntimeError(f"Dataset not found: {DATA_ROOT}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device : {device}")
    print(f"Layer        : {args.layer}")
    print(f"Type         : {args.type}")
    print(f"Model        : {MODEL_PATH}")

    checkpoint  = torch.load(MODEL_PATH, map_location=device)
    classes     = checkpoint["classes"]
    num_classes = checkpoint["num_classes"]

    print(f"\nClasses ({num_classes}): {classes}")
    print(f"Saved from epoch {checkpoint['epoch']} with val acc {checkpoint['val_acc']:.2f}%\n")

    model = TileCNN(num_classes=num_classes).to(device)
    model.load_state_dict(checkpoint["model_state"])
    model.eval()

    transform   = transforms.Compose([transforms.Resize((128,128)), transforms.ToTensor()])
    val_dataset = datasets.ImageFolder(os.path.join(DATA_ROOT, "val"), transform=transform)

    if len(val_dataset) == 0:
        raise RuntimeError("Val dataset is empty.")
    if val_dataset.classes != classes:
        raise RuntimeError(f"Class mismatch!\n  Model: {classes}\n  Val: {val_dataset.classes}")

    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False, num_workers=0)
    print(f"Val size: {len(val_dataset)}\n")

    matrix = np.zeros((num_classes, num_classes), dtype=int)
    with torch.no_grad():
        for imgs, labels in val_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            _, predicted = torch.max(model(imgs), 1)
            for true, pred in zip(labels.cpu().numpy(), predicted.cpu().numpy()):
                matrix[true, pred] += 1

    total_correct = np.trace(matrix)
    total         = matrix.sum()
    print(f"Overall val accuracy: {100.0*total_correct/total:.2f}%  ({total_correct}/{total})\n")

    print_per_class_accuracy(matrix, classes)
    print_top_confusions(matrix, classes, top_n=10)
    if args.matrix:
        print_confusion_matrix(matrix, classes)


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate a trained tile classifier")
    parser.add_argument("--layer", required=True, choices=["1","2","3"])
    parser.add_argument("--type",  required=True,
                        choices=["group","suit_type","honor_type","bonus_type",
                                 "char","bam","dot","wind","dragon"])
    parser.add_argument("--matrix", action="store_true",
                        help="Print full confusion matrix")
    args = parser.parse_args()
    evaluate(args)
