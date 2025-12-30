from collections import Counter

SUITS = ["DOT", "CHAR", "BAM"]
NUMBERS = list(range(1, 10))
DRAGONS = ["GREEN", "RED", "WHITE"]
WINDS = ["EAST", "SOUTH", "WEST", "NORTH"]

ALL_TILES = []

for suit in SUITS:
    for num in range(1, 10):
        ALL_TILES.append(f"{num}_{suit}")

for d in DRAGONS:
    ALL_TILES.append(f"{d}")

for w in WINDS:
    ALL_TILES.append(f"{w}")

NUM_TILE_TYPES = len(ALL_TILES)
ENCODED_SIZE = NUM_TILE_TYPES * 2


def encode_hand(hand_obj):
    """
    Encode hand as:
    [ concealed counts | displayed counts ]
    """
    arr = [0] * ENCODED_SIZE

    concealed = Counter(hand_obj.get("concealed", {}))
    display = Counter(hand_obj.get("display", {}))

    # concealed part
    for i, tile in enumerate(ALL_TILES):
        arr[i] = concealed.get(tile, 0)

    # displayed part
    offset = NUM_TILE_TYPES
    for i, tile in enumerate(ALL_TILES):
        arr[offset + i] = display.get(tile, 0)

    return arr


def encode_single_tile(tile):
    try:
        return ALL_TILES.index(tile)
    except ValueError:
        return None