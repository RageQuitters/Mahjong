# encoder.py
from collections import Counter

# All possible tiles in standard Singapore/Mahjong set
SUITS = ["DOT", "CHAR", "BAM"]
NUMBERS = list(range(1, 10))
DRAGONS = ["GREEN", "RED", "WHITE"]
WINDS = ["EAST", "SOUTH", "WEST", "NORTH"]

# Create a list of all possible tiles as strings
ALL_TILES = []

# Numbered tiles
for suit in SUITS:
    for num in NUMBERS:
        ALL_TILES.append(f"{num}_{suit}")

# Dragons
for dragon in DRAGONS:
    ALL_TILES.append(f"{dragon}_DRAGON")

# Winds
for wind in WINDS:
    ALL_TILES.append(f"{wind}_WIND")

# Total number of tile types
NUM_TILE_TYPES = len(ALL_TILES)


def encode_hand(hand_obj):
    """
    Encode a hand into a numerical array of size NUM_TILE_TYPES.
    Each index shows the count of that tile in the hand (concealed + displayed).
    """
    arr = [0] * NUM_TILE_TYPES

    combined = Counter(hand_obj.get("concealed", {}))
    combined.update(hand_obj.get("display", {}))

    for i, tile in enumerate(ALL_TILES):
        arr[i] = combined.get(tile, 0)

    return arr


def encode_single_tile(tile):
    """
    Encode a single tile to its array index
    """
    try:
        return ALL_TILES.index(tile)
    except ValueError:
        return None
