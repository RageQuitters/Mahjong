"""
Singapore Mahjong Discard Predictor API
========================================
POST /predict
  Body: HandRequest  (concealed, flowers, display)
  Returns: DiscardResponse or WinResponse

The "best_discard" field in DiscardResponse is always a decoded tile
name (e.g. "3_DOT", "RED", "EAST") that exists in the input concealed list.
"""

from fastapi import FastAPI, HTTPException

from api.schemas import HandRequest, PredictionResponse
from engine.model import predict_best_discard
import representation.hand as hand
from representation.all_tiles import ALL_TILES, BONUS_TILES


app = FastAPI(
    title="Singapore Mahjong Discard Predictor",
    version="2.0.0",
    description=(
        "Predicts the best tile to discard from a Singapore Mahjong hand. "
        "Returns the decoded tile name (e.g. '3_DOT', 'RED', 'EAST'). "
        "If the hand is already winning, returns the tai score and breakdown."
    ),
)

VALID_TILES = set(ALL_TILES)
BONUS_SET   = set(BONUS_TILES)


def _validate_tiles(tiles: list[str], field: str):
    for t in tiles:
        if t not in VALID_TILES and t not in BONUS_SET:
            raise HTTPException(
                status_code=422,
                detail=f"Unknown tile '{t}' in field '{field}'. "
                       f"Valid tiles: {sorted(VALID_TILES)}"
            )


@app.post("/predict", response_model=PredictionResponse)
def predict(req: HandRequest):
    """
    Predict the best discard for a Singapore Mahjong hand.

    - **concealed**: list of tile names in hand (e.g. ["1_DOT","2_DOT","RED"])
    - **flowers**: bonus tiles already collected (e.g. ["blue_1","cat"])
    - **display**: tiles shown as melds (pong/kong/chi) face-up

    Returns the best tile to discard (decoded name), or tai breakdown if winning.
    """
    _validate_tiles(req.concealed, "concealed")
    _validate_tiles(req.flowers,   "flowers")
    _validate_tiles(req.display,   "display")

    my_hand = hand.encode_hand(req.concealed, req.flowers, req.display)
    result  = predict_best_discard(my_hand)
    return result
