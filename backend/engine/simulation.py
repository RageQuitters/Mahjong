import numpy as np
import joblib  # for loading scikit-learn models
import rules.win_checker as win_checker
import rules.tai_calc as tai_calc

# TILE_ORDER should match your training encoding
from engine.encoder import TILE_ORDER, encode_hand_to_array

# Load your trained scikit-learn model
MODEL_PATH = "ml_model.pkl"
model = joblib.load(MODEL_PATH)

def best_discard_or_tai(hand_obj):
    """
    If the hand is winning, return the tai.
    Otherwise, predict the best discard using the trained ML model.
    """
    # 1️⃣ Winning check
    if win_checker.is_winning(hand_obj):
        return {"winning": True, "tai": tai_calc.calculate_tai(hand_obj)}

    # 2️⃣ Encode the hand as array
    input_array = encode_hand_to_array(hand_obj)  # shape: (34,)
    input_array = input_array.reshape(1, -1)  # sklearn expects 2D input

    # 3️⃣ Model prediction
    # The model should output a score or probability for each tile in concealed
    pred_scores = model.predict_proba(input_array)[0]  # shape: (34, n_classes)
    # If it's regression, just use model.predict(input_array)

    # 4️⃣ Choose best discard among tiles in concealed
    concealed_tiles = hand_obj["concealed"]
    best_tile = None
    best_score = -np.inf

    for i, tile in enumerate(TILE_ORDER):
        if tile in concealed_tiles:
            score = pred_scores[i] if pred_scores.ndim == 1 else pred_scores[i].max()
            if score > best_score:
                best_score = score
                best_tile = tile

    return {"winning": False, "best_discard": best_tile}