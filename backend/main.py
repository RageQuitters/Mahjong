# main.py
import representation.hand as hand
import representation.wall as wall
import representation.all_tiles as all_tiles
import rules.win_checker as win_checker
import rules.tai_calc as tai_calc
import engine.encoder
import engine.data.data_loader as dl
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

import csv
import random
from collections import Counter
from engine.encoder import ALL_TILES
import engine.data.data_gui_tool as gui
import tkinter as tk

MODEL_PATH = "best_discard_model.joblib"  # your trained ML model

def train_best_discard_model(csv_path, model_path="best_discard_model.joblib", max_rows = None):
    """
    Train a RandomForestClassifier to predict the best discard in Mahjong.
    
    Args:
        csv_path (str): Path to the CSV containing training data.
        model_path (str): Path where the trained model will be saved.
    
    Returns:
        float: Test accuracy
    """
    # -------------------------
    # Load data
    # -------------------------
    X, y = dl.load_training_data(csv_path, max_rows)
    print(f"Loaded {len(X)} examples.")

    # -------------------------
    # Split into train/test
    # -------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # -------------------------
    # Create and train the model
    # -------------------------
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # -------------------------
    # Evaluate
    # -------------------------
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Test Accuracy: {acc:.2f}")

    # -------------------------
    # Save the trained model
    # -------------------------
    joblib.dump(model, model_path)
    print(f"Model saved as {model_path}")
    return acc

def predict_best_discard(hand_obj):
    # 1️⃣ Check if hand is winning
    if win_checker.is_winning(hand_obj):
        tai_info = tai_calc.calculate_tai(hand_obj)
        return {"winning": True, "tai": tai_info}

    # 2️⃣ Encode hand for model
    encoded_hand = engine.encoder.encode_hand(hand_obj)

    # 3️⃣ Load trained ML model
    model = joblib.load(MODEL_PATH)

    # 4️⃣ Predict best discard
    discard_index = model.predict([encoded_hand])[0]

    # 5️⃣ Map index back to tile
    discard_tile = sorted(hand_obj["concealed"], key=lambda x: all_tiles.ALL_TILES.index(x))[discard_index]

    return {"winning": False, "best_discard": discard_tile}

def generate_random_hand():
    """
    Generate a random valid concealed Mahjong hand of 14 tiles.
    """
    counts = Counter()
    hand = []

    while len(hand) < 14:
        tile = random.choice(ALL_TILES)
        if counts[tile] < 4:
            counts[tile] += 1
            hand.append(tile)

    return hand

import csv
import random

SUITS = ["BAM", "CHAR", "DOT"]
NUMBERS = list(range(1, 10))
WINDS = ["EAST", "SOUTH", "WEST", "NORTH"]
DRAGONS = ["RED", "GREEN", "WHITE"]
FLOWERS = ["blue_1", "red_1",
        "blue_2", "red_2",
        "blue_3", "red_3",
        "blue_4", "red_4",
        "chicken", "cat", "centipede", "rat"]

ALL_TILES = [f"{n}_{s}" for s in SUITS for n in NUMBERS] + WINDS + DRAGONS

def write_random_hands_to_csv(csv_path, num_hands=1000):
    """
    Generate valid Mahjong hands with optional displayed melds and flowers,
    then write to a CSV file with empty best_discard for manual labeling.
    
    Args:
        csv_path (str): Path to output CSV file
        num_hands (int): Number of hands to generate
    """
    
    def draw_tile(available):
        tile = random.choice([t for t, c in available.items() if c > 0])
        available[tile] -= 1
        return tile

    def generate_random_hand():
        available = {t: 4 for t in ALL_TILES}
        display = []

        # Randomly decide 0-2 displayed melds
        num_melds = random.randint(0, 2)
        for _ in range(num_melds):
            meld_type = random.choice(["chi", "pong"])
            if meld_type == "pong":
                tiles = [t for t, c in available.items() if c >= 3]
                if not tiles:
                    continue
                t = random.choice(tiles)
                for _ in range(3):
                    available[t] -= 1
                display += [t, t, t]
            elif meld_type == "chi":
                suit = random.choice(SUITS)
                start = random.randint(1, 7)
                tiles = [f"{start}_{suit}", f"{start+1}_{suit}", f"{start+2}_{suit}"]
                if all(available[t] > 0 for t in tiles):
                    for t in tiles:
                        available[t] -= 1
                    display += tiles

        # Concealed tiles to reach 14
        concealed_count = 14 - len(display)
        concealed = [draw_tile(available) for _ in range(concealed_count)]
        concealed.sort(key = lambda x: ALL_TILES.index(x))

        # Random flowers/animals
        flowers = random.sample(FLOWERS, k=random.randint(0, 2))

        return concealed, display, flowers

    # Write to CSV
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        for _ in range(num_hands):
            c, d, flds = generate_random_hand()
            writer.writerow([
                ";".join(c),
                ";".join(d),
                ";".join(flds),
                ""  # best_discard left empty
            ])
    
    print(f"✅ Generated {num_hands} hands and wrote to {csv_path}")

def main():
    # 1️⃣ Create a full wall
    tile_wall = wall.create_full_wall()
    print("Total tiles in wall initially:", sum(tile_wall.values()))

    # 2️⃣ Sample hand
    concealed_list = [
    "2_BAM","3_DOT","6_DOT",
    "1_BAM","3_BAM","4_BAM",
    "6_CHAR","7_CHAR","8_CHAR",
    "9_DOT","9_DOT",
    "2_BAM","SOUTH", "WHITE",   # pair
]

    my_hand = hand.encode_hand(
        concealed_list,
        flowers_list=["blue_1", "red_3", "chicken"],
        display_list=[]
    )
    print("Initial hand:", my_hand)

    # 3️⃣ Remove hand tiles from wall
    tile_wall = wall.remove_hand_from_wall(tile_wall, my_hand)
    print("Tiles left in wall after removing hand:", sum(tile_wall.values()))

    # 4️⃣ Predict best discard
    result = predict_best_discard(my_hand)
    if result["winning"]:
        print("Hand is winning! Tai info:", result["tai"])
    else:
        print("Best discard suggested by ML model:", result["best_discard"])


if __name__ == "__main__":

    
    # GUI Tool for Manual Labelling
    root = tk.Tk()
    app = gui.MahjongEditor(root)
    root.mainloop()
    
    
    '''
    # Write hands to csv file for Manual Labelling
    write_random_hands_to_csv(
        "backend/engine/data/raw_data.csv",
        num_hands=1000
    )
    '''
    
    # Train Discard Model
    '''
    X, y = dl.load_training_data("backend/engine/data/raw_data.csv", max_rows = 55)
    print(f"Loaded {len(X)} examples.")
    if len(X) > 0:
        print("First encoded hand:", X[0])
        print("First target discard index:", y[0])
    train_best_discard_model("backend/engine/data/raw_data.csv", max_rows = 55)
    main()
    '''
    
    
