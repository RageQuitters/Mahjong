# ============================================================
# Singapore Mahjong — Canonical Tile Definitions
# 148-tile set: 136 playable + 8 flowers + 4 animals
# ============================================================

SUITS = ["DOT", "CHAR", "BAM"]          # Circle / Million / Bamboo
NUMBERS = list(range(1, 10))

# Honor tiles (playable as pong/kong/eye, never chow)
WINDS = ["EAST", "SOUTH", "WEST", "NORTH"]
DRAGONS = ["RED", "GREEN", "WHITE"]

# Bonus tiles (never discarded; drawn → show → replace)
# Flowers: blue_1–4 (season set) and red_1–4 (flower set)
# Animals: cat, rat, chicken, centipede
FLOWERS = [
    "blue_1", "red_1",
    "blue_2", "red_2",
    "blue_3", "red_3",
    "blue_4", "red_4",
]
ANIMALS = ["cat", "rat", "chicken", "centipede"]

BONUS_TILES = FLOWERS + ANIMALS

# ---- Ordered list used for model encoding ----
# Suit tiles first (DOT 1-9, CHAR 1-9, BAM 1-9), then winds, then dragons
ALL_TILES = (
    [f"{n}_{s}" for s in SUITS for n in NUMBERS]
    + WINDS
    + DRAGONS
)

NUM_TILE_TYPES = len(ALL_TILES)   # 34

# Convenience sets
HONOR_TILES = set(WINDS + DRAGONS)
SUIT_TILES  = set(ALL_TILES) - HONOR_TILES
