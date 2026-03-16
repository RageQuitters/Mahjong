from collections import Counter
from typing import List, Dict, Optional

# ----------------------------------------------------------------
# Hand Representation
# A hand is a dict:
#   "concealed" : Counter  – tiles in hand (can be discarded/drawn)
#   "display"   : Counter  – melded sets (pong/kong/chi) shown face-up
#   "flowers"   : Counter  – flower & animal bonus tiles collected
# ----------------------------------------------------------------

def encode_hand(
    tile_list: List[str],
    flowers_list: Optional[List[str]] = None,
    display_list: Optional[List[str]] = None,
) -> Dict[str, Counter]:
    """
    Build a hand dict from flat tile lists.
    """
    return {
        "concealed": Counter(tile_list),
        "display":   Counter(display_list or []),
        "flowers":   Counter(flowers_list or []),
    }


def possible_discards(hand: Dict[str, Counter]) -> List[str]:
    """Tiles in the concealed hand that can be discarded (unique)."""
    return [tile for tile, count in hand["concealed"].items() if count > 0]


def remove_tile(hand: Dict[str, Counter], tile: str) -> Dict[str, Counter]:
    """Return a new hand with one copy of *tile* removed from concealed."""
    new_concealed = hand["concealed"].copy()
    if new_concealed[tile] > 0:
        new_concealed[tile] -= 1
        if new_concealed[tile] == 0:
            del new_concealed[tile]
    return {**hand, "concealed": new_concealed}


def add_tile(hand: Dict[str, Counter], tile: str) -> Dict[str, Counter]:
    """Return a new hand with one copy of *tile* added to concealed."""
    new_concealed = hand["concealed"].copy()
    new_concealed[tile] += 1
    return {**hand, "concealed": new_concealed}
