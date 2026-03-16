"""
Singapore Mahjong – Discard Predictor
======================================
Thin module kept for API compatibility.
All prediction is now done via the heuristic — no ML model required.
"""

import rules.win_checker as win_checker
import rules.tai_calc    as tai_calc
from engine.heuristic import best_discard


def predict_best_discard(hand_obj: dict) -> dict:
    """
    Returns:
      Winning hand → {"winning": True,  "tai": int, "breakdown": list[str]}
      Otherwise    → {"winning": False, "best_discard": str}

    "best_discard" is always a decoded tile name (e.g. "3_DOT", "RED", "EAST")
    that exists in hand_obj["concealed"].
    """
    if win_checker.is_winning(hand_obj):
        calc = tai_calc.calculate_tai(hand_obj)
        return {
            "winning":   True,
            "tai":       calc["tai"],
            "breakdown": calc["breakdown"],
        }

    return {
        "winning":      False,
        "best_discard": best_discard(hand_obj),
    }
