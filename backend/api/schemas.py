from pydantic import BaseModel
from typing import List, Optional, Union


class HandRequest(BaseModel):
    """
    Request body for /predict.

    concealed : tiles in the player's hand (14 tiles for a fresh turn,
                fewer if melds have been displayed)
    flowers   : bonus flower/animal tiles already collected (optional)
    display   : tiles already shown face-up as melds – pong = 3 copies,
                kong = 4 copies, chow = 3 consecutive copies (optional)
    """
    concealed: List[str]
    flowers:   Optional[List[str]] = []
    display:   Optional[List[str]] = []


class DiscardResponse(BaseModel):
    """Returned when the hand is NOT yet complete."""
    winning:      bool = False
    # Decoded tile name, e.g. "3_DOT", "RED", "EAST"
    best_discard: str


class WinResponse(BaseModel):
    """Returned when the hand IS a winning hand."""
    winning:   bool = True
    tai:       int
    breakdown: List[str]


PredictionResponse = Union[DiscardResponse, WinResponse]
