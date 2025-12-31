from fastapi import FastAPI
from api.schemas import HandRequest, DiscardResponse
from engine.model import predict_best_discard
import representation.hand as hand

app = FastAPI(
    title="Mahjong Best Discard API",
    version="1.0.0"
)

@app.post("/predict", response_model=DiscardResponse)
def predict(req: HandRequest):
    my_hand = hand.encode_hand(req.concealed, req.flowers, req.display)
    return predict_best_discard(my_hand)