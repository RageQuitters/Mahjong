# representation/wall.py
from collections import Counter
from typing import List, Dict
import random

def create_full_wall(include_flowers: bool = True) -> Counter:
    """
    Create a full Mahjong tile set as a Counter.
    By default includes 4 copies of each suited tile, winds, dragons, and optionally flowers.
    """
    tiles = []

    # Suits
    for n in range(1, 10):
        tiles += [f"{n}_DOT"] * 4
        tiles += [f"{n}_CHAR"] * 4
        tiles += [f"{n}_BAM"] * 4

    # Winds and Dragons
    tiles += ["east", "south", "west", "north"] * 4
    tiles += ["red", "green", "white"] * 4

    # Flowers (optional)
    if include_flowers:
        tiles += [f"flower{i}" for i in range(1, 9)]  # 8 flowers total

    return Counter(tiles)

def remove_hand_from_wall(tile_wall: Counter, hand: Dict[str, Counter]) -> Counter:
    """
    Returns a new Counter representing the wall after removing the tiles
    in the given hand (concealed, melded, and flowers).
    """
    remaining = tile_wall.copy()
    remaining.subtract(hand["concealed"])
    remaining.subtract(hand["display"])
    remaining.subtract(hand["flowers"])
    return remaining

def draw_tile(tile_wall: Counter) -> str:
    """
    Randomly draws a tile from the wall according to remaining counts.
    Returns the tile string and updates the wall.
    """
    if sum(tile_wall.values()) == 0:
        raise ValueError("No tiles left in the wall")

    # Flatten the Counter into a list weighted by count
    all_tiles = list(tile_wall.elements())
    tile = random.choice(all_tiles)

    # Decrement the count
    tile_wall[tile] -= 1
    if tile_wall[tile] == 0:
        del tile_wall[tile]

    return tile

def wall_to_list(tile_wall: Counter) -> List[str]:
    """
    Converts the Counter representation of the wall into a flat list of tiles.
    """
    return list(tile_wall.elements())
