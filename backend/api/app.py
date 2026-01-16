import shutil
import uuid
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from api.schemas import HandRequest, PredictionResponse
from engine.model import predict_best_discard
import representation.hand as hand

'''
# Image tile detection
from vision.detect_tiles import run_tile_dectection
'''


app = FastAPI(
    title="Mahjong Best Discard API",
    version="1.0.0"
)

UPLOAD_DIR = Path("vision/tile_images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------
# JSON-based prediction
# -------------------------
@app.post("/predict", response_model=PredictionResponse)
def predict(req: HandRequest):
    my_hand = hand.encode_hand(
        req.concealed,
        req.flowers,
        req.display
    )
    return predict_best_discard(my_hand)

'''
# -------------------------
# IMAGE-based prediction
# -------------------------
@app.post("/image", response_model=PredictionResponse)
async def predict_from_image(file: UploadFile = File(...)):

    if file.content_type not in ["image/jpeg", "image/jpg"]:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG images are supported"
        )

    # 1. Save uploaded image
    img_path = UPLOAD_DIR / f"{uuid.uuid4()}.jpg"
    try:
        with open(img_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Run tile detection (PASS PATH)
        detected = tile_detector.run_tile_detection(str(img_path))

        # 🔴 Adjust this mapping if needed
        my_hand = hand.encode_hand(
            detected["concealed"],
            detected.get("flowers", []),
            detected.get("display", [])
        )

        # 3. Predict
        return predict_best_discard(my_hand)

    finally:
        # 4. Always clean up
        img_path.unlink(missing_ok=True)
'''