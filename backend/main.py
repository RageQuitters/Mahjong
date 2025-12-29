# main.py
import representation.hand as hand
import representation.wall as wall
import rules.win_checker as win_checker
import rules.tai_calc as tai_calc
import engine.encoder
import joblib

MODEL_PATH = "best_discard_model.joblib"  # your trained ML model
ENCODER_PATH = "encoder.pkl"              # your encoder if needed

def predict_best_discard(hand_obj):
    # 1️⃣ Check if hand is winning
    if win_checker.is_winning(hand_obj):
        tai_info = tai_calc.calculate_tai(hand_obj)
        return {"winning": True, "tai": tai_info}

    # 2️⃣ Encode hand for model
    encoded_hand = engine.encoder.encode_hand(hand_obj)

    # 3️⃣ Load trained ML model
    #model = joblib.load(MODEL_PATH)

    # 4️⃣ Predict best discard
    #discard_index = model.predict([encoded_hand])[0]

    # Temp Dummy Model that discards the first card
    class DummyModel:
        def predict(self, X):
            return [0]  # always pick the first possible discard

    model = DummyModel()

    # 4️⃣ Predict best discard
    discard_index = model.predict([encoded_hand])[0]

    # 5️⃣ Map index back to tile
    possible_discards = hand.possible_discards(hand_obj)
    if discard_index >= len(possible_discards):
        # fallback in case of mismatch
        discard_tile = possible_discards[0]
    else:
        discard_tile = possible_discards[discard_index]

    return {"winning": False, "best_discard": discard_tile}


def main():
    # 1️⃣ Create a full wall
    tile_wall = wall.create_full_wall()
    print("Total tiles in wall initially:", sum(tile_wall.values()))

    # 2️⃣ Sample hand
    concealed_list = [
        "1_BAM","9_BAM",
        "1_CHAR","9_CHAR",
        "1_DOT","9_DOT",
        "EAST","SOUTH","WEST","NORTH",
        "RED","GREEN","WHITE",
        "2_CHAR"  # pair
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
    main()
