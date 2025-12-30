import csv
import representation.hand as hand
import representation.all_tiles as all_tiles
from engine.encoder import encode_hand, encode_single_tile

def parse_tiles(tile_str):
    if not tile_str:
        return []
    return [t.strip() for t in tile_str.split(";") if t.strip()]

def load_training_data(csv_path, max_rows = None):
    X = []
    y = []

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i,row in enumerate(reader):
            if max_rows is not None and i >= max_rows:
                break
            concealed = parse_tiles(row["concealed"])
            display = parse_tiles(row["display"])
            flowers = parse_tiles(row["flowers"])
            best_discard = row["best_discard"].strip()

            hand_obj = hand.encode_hand(
                concealed,
                display_list=display,
                flowers_list=flowers
            )

            encoded = encode_hand(hand_obj)
            X.append(encoded)
            sorted_concealed = sorted(concealed, key = lambda x: all_tiles.ALL_TILES.index(x))
            if best_discard not in sorted_concealed:
                y.append(0)
            else:
                discard_idx = sorted_concealed.index(best_discard)
                y.append(discard_idx)
    return X, y
