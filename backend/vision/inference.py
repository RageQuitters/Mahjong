import torch
from PIL import Image
import torchvision.transforms as T
from model import TileCNN

MODEL_PATH = "tile_cnn.pth"
IMAGE_SIZE = 128

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

checkpoint = torch.load(MODEL_PATH, map_location=device)
classes = checkpoint["classes"]
num_classes = len(classes)
print("Classes in checkpoint:", checkpoint["classes"])

model = TileCNN(num_classes).to(device)
model.load_state_dict(checkpoint["model_state"])
model.eval()

transform = T.Compose([
    T.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    T.ToTensor()
])

def classify_tile_image(tile_img_np):
    """
    tile_img_np: numpy array (RGB crop from extract_tile_images)
    """
    img = Image.fromarray(tile_img_np).convert("RGB")
    img = transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        logits = model(img)
        pred = logits.argmax(dim=1).item()

    return classes[pred]
