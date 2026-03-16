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

# -------------------------
# CV name → encoder name
# -------------------------
# The CV classifier uses names like "GREEN_DRAGON", "RED_DRAGON", "WHITE_DRAGON"
# and layer-3 suit outputs like "1_char", "3_bam", "5_dot" (lowercase).
# This maps those to the canonical encoder names.

_CV_NAME_MAP = {
    # Dragons
    "GREEN_DRAGON": "GREEN",
    "RED_DRAGON":   "RED",
    "WHITE_DRAGON": "WHITE",
    # Winds (already match, but included for safety)
    "EAST":  "EAST",
    "SOUTH": "SOUTH",
    "WEST":  "WEST",
    "NORTH": "NORTH",
}

# Suit tiles from CV come out as e.g. "3_bam", "1_char", "9_dot" (lowercase suit)
# We normalise them to "3_BAM", "1_CHAR", "9_DOT"
def _normalise_cv_name(cv_name: str) -> str | None:
    """
    Convert a CV class_name to the canonical encoder tile name.
    Returns None if the tile is a bonus tile (flower/animal) or unrecognised.
    """
    # Direct lookup first
    if cv_name in _CV_NAME_MAP:
        return _CV_NAME_MAP[cv_name]

    # Already canonical (e.g. "GREEN", "EAST", "3_BAM")
    if cv_name in ALL_TILES:
        return cv_name

    # Uppercase and try again (handles "3_bam" → "3_BAM")
    upper = cv_name.upper()
    if upper in ALL_TILES:
        return upper

    # Bonus tiles — caller should handle separately
    if cv_name in ("flower", "animal"):
        return None

    # Unknown — skip gracefully
    return None


def cv_results_to_hand(cv_results: list[dict]) -> dict:
    """
    Convert the list of dicts returned by classify_image() into a hand dict
    ready for encode_hand().

    CV output format:
        [{"box": (x1,y1,x2,y2), "class_name": "3_BAM"}, ...]

    Returns:
        {
            "concealed": {"3_BAM": 2, "EAST": 1, ...},
            "flowers":   ["flower", "flower"],      # bonus tiles
            "display":   {}
        }

    Rules:
        - bonus tiles (flower / animal) → flowers list
        - all other recognised tiles    → concealed counts
    """
    concealed = Counter()
    flowers = []

    for item in cv_results:
        cv_name = item.get("class_name", "")

        if cv_name in ("flower", "animal"):
            flowers.append(cv_name)
            continue

        canonical = _normalise_cv_name(cv_name)
        if canonical is not None:
            concealed[canonical] += 1
        # else: unrecognised tile — skip silently

    return {
        "concealed": dict(concealed),
        "flowers":   Counter({"bonus": len(flowers)}),
        "display":   {},
    }

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
