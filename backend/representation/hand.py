from collections import Counter
from typing import List, Dict

# ----------------------------
# Hand Representation & Helpers
# ----------------------------

def encode_hand(
    tile_list: List[str],
    flowers_list: List[str] = None,
    display_list: List[str] = None
) -> Dict[str, Counter]:
    """
    Encode a Mahjong hand into a dictionary with three parts:
    - 'concealed': tiles in hand that can be discarded/drawn
    - 'display': revealed sets (Pong/Kong/Chi)
    - 'flowers': flower/bonus tiles collected

    Args:
        tile_list: List of concealed tiles
        flowers_list: List of flowers (optional)
        melded_list: List of melded tiles (optional)

    Returns:
        Dictionary with keys 'concealed', 'melded', 'flowers'
    """
    return {
        "concealed": Counter(tile_list),
        "display": Counter(display_list or []),
        "flowers": Counter(flowers_list or [])
    }

def possible_discards(hand: Dict[str, Counter]) -> List[str]:
    """
    Returns the list of tiles in the concealed hand that can be discarded.
    """
    return [tile for tile, count in hand["concealed"].items() if count > 0]

def remove_tile(hand: Dict[str, Counter], tile: str) -> Dict[str, Counter]:
    """
    Returns a new hand dictionary with one instance of the tile removed from concealed.
    Does not modify the original hand.
    """
    new_hand = hand.copy()
    new_hand["concealed"] = hand["concealed"].copy()
    if new_hand["concealed"][tile] > 0:
        new_hand["concealed"][tile] -= 1
        if new_hand["concealed"][tile] == 0:
            del new_hand["concealed"][tile]
    return new_hand

def add_tile(hand: Dict[str, Counter], tile: str) -> Dict[str, Counter]:
    """
    Returns a new hand dictionary with one instance of the tile added to concealed.
    """
    new_hand = hand.copy()
    new_hand["concealed"] = hand["concealed"].copy()
    new_hand["concealed"][tile] += 1
    return new_hand

def add_flower(hand: Dict[str, Counter], flower_tile: str) -> Dict[str, Counter]:
    """
    Returns a new hand dictionary with a flower tile added.
    """
    new_hand = hand.copy()
    new_hand["flowers"] = hand["flowers"].copy()
    new_hand["flowers"][flower_tile] += 1
    return new_hand
