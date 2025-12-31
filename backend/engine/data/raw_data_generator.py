# =========================
# Standard library imports
# =========================
import csv
import random
from collections import Counter

# =========================
# Third-party imports
# =========================
import pandas as pd

# =========================
# Constants
# =========================
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
# Random hand generation
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

            concealed = [draw_tile(pool) for _ in range(14)]
            concealed.sort(key=ALL_TILES.index)

            flowers = random.sample(FLOWERS, k=random.randint(0, 2))

            writer.writerow([
                ";".join(concealed),
                ";".join(display),
                ";".join(flowers),
                ""
            ])

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
    dominant_suit = max(suit_counts, key=suit_counts.get)

    scores = {}
    for t in set(tiles):
        count = tiles.count(t)

        if t in HONORS:
            score = 80 if count == 1 else 40
            if not has_flowers:
                score += 20
        else:
            val, suit = t.split("_")
            val = int(val)
            neighbors = {f"{val-1}_{suit}", f"{val+1}_{suit}"}
            isolated = count == 1 and not neighbors & set(tiles)

            score = 100 if isolated else 20
            if suit != dominant_suit:
                score += 10

        scores[t] = score

    return max(scores, key=scores.get)

def process_csv(input_path: str, output_path: str):
    df = pd.read_csv(input_path)
    mask = df["best_discard"].isna() | (df["best_discard"] == "")

    df.loc[mask, "best_discard"] = df[mask].apply(
        lambda r: calculate_best_discard(r["concealed"], r.get("flowers")),
        axis=1
    )

    df.to_csv(output_path, index=False)