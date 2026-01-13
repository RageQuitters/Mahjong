import torch
from torch.utils.data import DataLoader
import torch.optim as optim
import torch.nn as nn

from dataset import MahjongTileDataset
from model import TileCNN
from pathlib import Path


# --------- CONFIGURATION ----------------
DATASET_ROOT = "dataset"
IMAGE_SIZE = 128
BATCH_SIZE = 64
EPOCHS = 75
LR = 1e-4
MODEL_OUT = "tile_cnn.pth"
# ----------------------------------------

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

train_ds = MahjongTileDataset(Path(DATASET_ROOT)/"train", IMAGE_SIZE)
val_ds = MahjongTileDataset(Path(DATASET_ROOT)/"val", IMAGE_SIZE)

x, y = train_ds[0]
print(x.shape, y)
print(x.min(), x.max())  # should be 0.0–1.0 if transformed to tensor
print(list(train_ds.class_to_idx.keys())[y])

num_classes = len(list(train_ds.class_to_idx.keys()))

train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE)

model = TileCNN(num_classes).to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LR)



# ---------------- TRAIN LOOP ----------------
for epoch in range(EPOCHS):
    model.train()
    total_loss = 0

    for imgs, labels in train_loader:
        imgs, labels = imgs.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(imgs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    # Validation
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for imgs, labels in val_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            outputs = model(imgs)
            preds = outputs.argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

    acc = correct / total * 100
    print(f"Epoch {epoch+1}/{EPOCHS} | Loss {total_loss:.3f} | Val Acc {acc:.2f}%")

torch.save({
    "model_state": model.state_dict(),
    "classes": list(train_ds.class_to_idx.keys())
}, MODEL_OUT)

print("Model saved to", MODEL_OUT)

