import io
from pathlib import Path

import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from schemas import HandRequest, PredictionResponse
from engine.model import predict_best_discard
from engine.encoder import cv_results_to_hand
import representation.hand as hand

from vision.classify import classify_image


app = FastAPI(
    title="Mahjong Best Discard API",
    version="1.0.0"
)

UPLOAD_DIR = Path("vision/tile_images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

_CV_TO_CANONICAL = {
    "RED_DRAGON": "RED",
    "GREEN_DRAGON": "GREEN",
    "WHITE_DRAGON": "WHITE",
}


# -------------------------
# Shared helpers
# -------------------------
async def _decode_image(file: UploadFile) -> np.ndarray:
    if file.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG and PNG images are supported"
        )
    raw = await file.read()
    np_arr = np.frombuffer(raw, np.uint8)
    image_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if image_bgr is None:
        raise HTTPException(
            status_code=422,
            detail="Could not decode image. Make sure it is a valid JPEG or PNG."
        )
    return image_bgr


def _run_pipeline(image_bgr: np.ndarray):
    """Run CV + AI pipeline. Returns (cv_results, prediction)."""
    cv_results = classify_image(image_bgr)
    if not cv_results:
        raise HTTPException(
            status_code=422,
            detail="No tiles were detected in the image."
        )
    print("CV results:", [r["class_name"] for r in cv_results])
    my_hand = cv_results_to_hand(cv_results)
    prediction = predict_best_discard(my_hand)
    print("Prediction:", prediction)
    
    return cv_results, prediction


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


# -------------------------
# IMAGE-based prediction (JSON response)
# -------------------------
@app.post("/image", response_model=PredictionResponse)
async def predict_from_image(file: UploadFile = File(...)):
    image_bgr = await _decode_image(file)
    _, prediction = _run_pipeline(image_bgr)
    return prediction


# -------------------------
# IMAGE-based prediction (visualised image response)
# -------------------------
@app.post("/image/visualise")
async def predict_from_image_visualise(file: UploadFile = File(...)):
    """
    Same as /image but returns a JPEG with the suggested discard tile
    highlighted in red. If the hand is already winning, all detected
    tiles are highlighted in gold instead.
    """
    image_bgr = await _decode_image(file)
    cv_results, prediction = _run_pipeline(image_bgr)

    vis = image_bgr.copy()

    if prediction.get("winning"):
        # Winning hand — highlight all tiles in gold
        for item in cv_results:
            x1, y1, x2, y2 = item["box"]
            cv2.rectangle(vis, (x1, y1), (x2, y2), (0, 215, 255), 3)
        cv2.putText(
            vis,
            f"WIN! Tai: {prediction.get('tai', '?')}",
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.4,
            (0, 215, 255),
            3,
        )
    else:
        best_discard = prediction.get("best_discard")

        for item in cv_results:
            x1, y1, x2, y2 = item["box"]
            canonical = _CV_TO_CANONICAL.get(item["class_name"], item["class_name"])
            if canonical == best_discard:
                # Red box + DISCARD label for the suggested tile
                cv2.rectangle(vis, (x1, y1), (x2, y2), (0, 0, 255), 3)
                cv2.putText(
                    vis,
                    "DISCARD",
                    (x1, max(0, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2,
                )
            else:
                # Subtle grey box for all other tiles
                cv2.rectangle(vis, (x1, y1), (x2, y2), (180, 180, 180), 1)

    # Encode result to JPEG and stream back
    success, buffer = cv2.imencode(".jpg", vis)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to encode output image.")

    return StreamingResponse(
        io.BytesIO(buffer.tobytes()),
        media_type="image/jpeg",
    )
