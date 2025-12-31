# =========================
# Standard library imports
# =========================
from pathlib import Path

# =========================
# Third-party imports
# =========================
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# =========================
# Project imports
# =========================
from representation import hand
import representation.all_tiles as all_tiles
import rules.win_checker as win_checker
import rules.tai_calc as tai_calc
import engine.encoder as encoder
import engine.data.data_loader as dl

# =========================
# Constants
# =========================
MODEL_PATH = Path(__file__).resolve().parent.parent.parent / "best_discard_model.joblib"
MODEL = None

# =========================
# Training
# =========================
def train_best_discard_model(
    csv_path: str,
    model_path: Path = MODEL_PATH,
    max_rows: int | None = None
) -> float:
    X, y = dl.load_training_data(csv_path, max_rows)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        min_samples_leaf=5,
        n_jobs=-1,
        random_state=42
    )

    model.fit(X_train, y_train)

    acc = accuracy_score(y_test, model.predict(X_test))
    joblib.dump(model, model_path)

    return acc

# =========================
# Prediction
# =========================
def predict_best_discard(hand_obj: dict) -> dict:
    if win_checker.is_winning(hand_obj):
        return {
            "winning": True,
            "tai": tai_calc.calculate_tai(hand_obj)
        }

    model = joblib.load(MODEL_PATH)
    encoded = encoder.encode_hand(hand_obj)

    discard_idx = model.predict([encoded])[0]
    concealed_sorted = sorted(
        hand_obj["concealed"],
        key=lambda t: all_tiles.ALL_TILES.index(t)
    )

    return {
        "winning": False,
        "best_discard": concealed_sorted[
            discard_idx % len(concealed_sorted)
        ]
    }
