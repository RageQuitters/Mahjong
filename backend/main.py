# =========================
# Standard library imports
# =========================
import csv
import random
from collections import Counter
from pathlib import Path

# =========================
# Third-party imports
# =========================
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# =========================
# Project imports
# =========================
import representation.hand as hand
import representation.wall as wall
import representation.all_tiles as all_tiles
import rules.win_checker as win_checker
import rules.tai_calc as tai_calc
import engine.encoder as encoder
import engine.data.data_loader as dl

# =========================
# Constants
# =========================
MODEL_PATH = Path("best_discard_model.joblib")

SUITS = ["BAM", "CHAR", "DOT"]
NUMBERS = range(1, 10)
WINDS = ["EAST", "SOUTH", "WEST", "NORTH"]
DRAGONS = ["RED", "GREEN", "WHITE"]

FLOWERS = [
    "blue_1", "red_1", "blue_2", "red_2",
    "blue_3", "red_3", "blue_4", "red_4",
    "chicken", "cat", "centipede", "rat"
]

ALL_TILES = [f"{n}_{s}" for s in SUITS for n in NUMBERS] + WINDS + DRAGONS
HONORS = set(WINDS + DRAGONS)

# =========================
# ML: Training
# =========================
def train_best_discard_model(
    csv_path: str,
    model_path: Path = MODEL_PATH,
    max_rows: int | None = None
) -> float:
    """
    Train a RandomForest model to predict the best discard.
    """
    X, y = dl.load_training_data(csv_path, max_rows)
    print(f"Loaded {len(X)} examples")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        min_samples_leaf=5,
        n_jobs=-1,
        verbose=2,
        random_state=42
    )

    model.fit(X_train, y_train)

    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"Test accuracy: {acc:.4f}")

    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

    return acc

# =========================
# ML: Prediction
# =========================
def predict_best_discard(hand_obj: dict) -> dict:
    """
    Predict the best discard for a given Mahjong hand.
    """
    if win_checker.is_winning(hand_obj):
        return {
            "winning": True,
            "tai": tai_calc.calculate_tai(hand_obj)
        }

    encoded = encoder.encode_hand(hand_obj)
    model = joblib.load(MODEL_PATH)

    discard_idx = model.predict([encoded])[0]
    concealed = sorted(
        hand_obj["concealed"],
        key=lambda t: all_tiles.ALL_TILES.index(t)
    )

    return {
        "winning": False,
        "best_discard": concealed[discard_idx % len(concealed)]
    }

# =========================
# Data generation
# =========================
def generate_random_concealed_hand() -> list[str]:
    counts = Counter()
    hand_tiles = []

    while len(hand_tiles) < 14:
        tile = random.choice(ALL_TILES)
        if counts[tile] < 4:
            counts[tile] += 1
            hand_tiles.append(tile)

    return hand_tiles

def write_random_hands_to_csv(csv_path: str, num_hands: int = 1_000):
    """
    Generate random Mahjong hands for labeling.
    """
    def draw_tile(pool):
        choices = [t for t, c in pool.items() if c > 0]
        tile = random.choice(choices)
        pool[tile] -= 1
        return tile

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)

        for _ in range(num_hands):
            pool = {t: 4 for t in ALL_TILES}
            display = []

            for _ in range(random.randint(0, 2)):
                meld = random.choice(["chi", "pong"])
                if meld == "pong":
                    tiles = [t for t, c in pool.items() if c >= 3]
                    if tiles:
                        t = random.choice(tiles)
                        pool[t] -= 3
                        display += [t] * 3

                else:  # chi
                    suit = random.choice(SUITS)
                    start = random.randint(1, 7)
                    tiles = [f"{start+i}_{suit}" for i in range(3)]
                    if all(pool[t] > 0 for t in tiles):
                        for t in tiles:
                            pool[t] -= 1
                        display += tiles

            concealed = [draw_tile(pool) for _ in range(14 - len(display))]
            concealed.sort(key=ALL_TILES.index)
            flowers = random.sample(FLOWERS, k=random.randint(0, 2))

            writer.writerow([
                ";".join(concealed),
                ";".join(display),
                ";".join(flowers),
                ""
            ])

    print(f"Generated {num_hands} hands → {csv_path}")

# =========================
# Heuristic labeling
# =========================
def calculate_best_discard(concealed: str, flowers: str | None) -> str | None:
    if not concealed or pd.isna(concealed):
        return None

    tiles = concealed.split(";")
    has_flowers = bool(flowers and not pd.isna(flowers))

    suit_counts = {
        s: sum(t.endswith(f"_{s}") for t in tiles)
        for s in SUITS
    }
    dominant_suit = max(suit_counts, key=suit_counts.get, default=None)

    scores = {}
    for t in set(tiles):
        count = tiles.count(t)

        if t in HONORS:
            score = 80 if count == 1 else 40
            if not has_flowers:
                score += 20
        else:
            try:
                val, suit = t.split("_")
                val = int(val)
                neighbors = {f"{val-1}_{suit}", f"{val+1}_{suit}"}
                isolated = count == 1 and not neighbors & set(tiles)

                score = 100 if isolated else 20
                if suit != dominant_suit:
                    score += 10
            except ValueError:
                score = 0

        scores[t] = score

    return max(scores, key=lambda t: (scores[t], t)) if scores else None

def process_csv(input_path: str, output_path: str):
    df = pd.read_csv(input_path)
    mask = df["best_discard"].isna() | (df["best_discard"] == "")

    df.loc[mask, "best_discard"] = df[mask].apply(
        lambda r: calculate_best_discard(r["concealed"], r.get("flowers")),
        axis=1
    )

    df.to_csv(output_path, index=False)
    print(f"Saved labeled CSV → {output_path}")

# =========================
# Demo / entry point
# =========================
def main():
    tile_wall = wall.create_full_wall()
    print("Tiles in wall:", sum(tile_wall.values()))

    concealed = [
    "1_BAM","EAST","3_BAM",
    "4_BAM","5_BAM","6_BAM",
    "7_BAM","8_BAM","9_BAM",
    "2_BAM","3_BAM","4_BAM",
    "5_BAM","5_BAM"
]

    my_hand = hand.encode_hand(concealed, flowers_list=["chicken"], display_list=[])
    tile_wall = wall.remove_hand_from_wall(tile_wall, my_hand)

    result = predict_best_discard(my_hand)
    print(result)

if __name__ == "__main__":
    main()
