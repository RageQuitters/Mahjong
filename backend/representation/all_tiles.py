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