from collections import Counter
from functools import lru_cache

SUITS = ["DOT", "CHAR", "BAM"]
DRAGONS = ["GREEN", "RED", "WHITE"]
WINDS = ["EAST", "SOUTH", "WEST", "NORTH"]

def is_winning(hand_obj) -> bool:
    """
    Check if the hand is a winning hand.
    - Includes both concealed and displayed tiles.
    - Pair must come from concealed tiles.
    """
    concealed = hand_obj["concealed"]
    display = hand_obj["display"]

    total_tiles = sum(concealed.values()) + sum(display.values())
    if total_tiles != 14:
        return False

    # Special hands
    if is_thirteen_wonders(concealed):
        return True

    # Standard 4 melds + 1 pair
    return is_standard_win(hand_obj)


def is_standard_win(hand_obj) -> bool:
    """
    Standard winning hand: 4 melds + 1 pair
    - Pair must be from concealed tiles
    - Displayed tiles count as committed melds
    """
    concealed = hand_obj["concealed"]
    display = hand_obj["display"]

    display_melds = sum(display.values()) // 3
    melds_needed = 4 - display_melds

    total_tiles_for_melds = Counter(concealed)

    # If all melds are already in display, just check for any pair in concealed
    if melds_needed == 0:
        for tile, count in concealed.items():
            if count >= 2:
                return True
        return False

    # Try every possible pair from concealed
    for tile, count in concealed.items():
        if count >= 2:
            remaining = total_tiles_for_melds.copy()
            remaining[tile] -= 2
            if remaining[tile] == 0:
                del remaining[tile]

            if can_form_melds(frozenset(remaining.items()), melds_needed):
                return True

    return False


@lru_cache(maxsize=None)
def can_form_melds(counter_frozen: frozenset, melds_needed: int) -> bool:
    """
    Recursively check if exactly 'melds_needed' melds can be formed from the counter
    """
    counter = Counter(dict(counter_frozen))

    if melds_needed == 0:
        # Must not have leftover tiles if melds are formed
        return len(counter) == 0

    if not counter:
        return False

    tile = min(counter)  # deterministic
    count = counter[tile]

    # Try pong
    if count >= 3:
        new_counter = counter.copy()
        new_counter[tile] -= 3
        if new_counter[tile] == 0:
            del new_counter[tile]

        if can_form_melds(frozenset(new_counter.items()), melds_needed - 1):
            return True

    # Try chow (only numeric suits)
    parts = tile.split("_")
    if len(parts) == 2 and parts[0].isdigit():
        num = int(parts[0])
        suit = parts[1]

        if suit in SUITS and num <= 7:
            t2 = f"{num+1}_{suit}"
            t3 = f"{num+2}_{suit}"
            if counter.get(t2, 0) >= 1 and counter.get(t3, 0) >= 1:
                new_counter = counter.copy()
                for t in [tile, t2, t3]:
                    new_counter[t] -= 1
                    if new_counter[t] == 0:
                        del new_counter[t]

                if can_form_melds(frozenset(new_counter.items()), melds_needed - 1):
                    return True

    return False


def is_thirteen_wonders(counter: Counter) -> bool:
    required = set()
    for suit in SUITS:
        required.add(f"1_{suit}")
        required.add(f"9_{suit}")
    for d in DRAGONS:
        required.add(f"{d}")
    for w in WINDS:
        required.add(f"{w}")

    tiles = set(counter.keys())

    # Must contain all 13 unique tiles
    if not required.issubset(tiles):
        return False

    # Exactly one pair among them
    pair_count = sum(1 for t in required if counter[t] == 2)
    return pair_count == 1
