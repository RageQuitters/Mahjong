"""
Singapore Mahjong – Win Checker
================================
Winning conditions:
  1. Standard:  4 melds (chow / pong / kong) + 1 pair (eye)
     - Pair MUST come from concealed tiles
     - Display tiles count as committed melds (pong/kong/chi of 3 or 4)
     - Kong (4 tiles) in display counts as ONE meld
  2. Thirteen Wonders (十三幺):  one each of the 13 terminals/honors + any
     one duplicate among them, all in concealed hand
  3. All 8 Flowers:  collecting all 8 flower/season tiles (instant win)

Minimum 1 tai required to declare a win (enforced by the caller / tai_calc).
"""

from collections import Counter
from functools import lru_cache

from representation.all_tiles import SUITS, DRAGONS, WINDS


# ------------------------------------------------------------------ #
#  Public API
# ------------------------------------------------------------------ #

def is_winning(hand_obj: dict) -> bool:
    """Return True if the hand constitutes a winning hand."""
    concealed: Counter = hand_obj["concealed"]
    display:   Counter = hand_obj["display"]
    flowers:   Counter = hand_obj.get("flowers", Counter())

    # All-8-flowers instant win
    if sum(flowers.values()) >= 8:
        return True

    # Thirteen Wonders
    if is_thirteen_wonders(concealed):
        return True

    # Standard 4 melds + 1 pair
    # Total playable tiles must be exactly 14
    total = sum(concealed.values()) + _display_tile_count(display)
    if total != 14:
        return False

    return _is_standard_win(concealed, display)


# ------------------------------------------------------------------ #
#  Standard win helper
# ------------------------------------------------------------------ #

def _display_tile_count(display: Counter) -> int:
    """Number of actual tiles in display (pong=3, kong=4)."""
    return sum(display.values())


def _display_meld_count(display: Counter) -> int:
    """
    Number of committed melds in display.
    Pong contributes 3 tiles → 1 meld.
    Kong contributes 4 tiles → 1 meld.
    Chi  contributes 3 tiles → 1 meld.
    We detect kongs by tiles with count == 4.
    """
    # Each distinct tile in display is one meld set (3 or 4 of the same tile)
    # For chi sequences the tiles appear individually (count 1 each per chow)
    # We trust the caller to pass display as individual tile counts.
    # A kong is when a tile appears 4 times in display.
    total_tiles = sum(display.values())
    # Pong/Chi sets = 3 tiles each, Kong = 4 tiles = 1 meld
    # Count kongs first
    kongs = sum(1 for t, c in display.items() if c == 4)
    remainder = total_tiles - kongs * 4  # remaining tiles in 3-tile melds
    return kongs + remainder // 3


def _is_standard_win(concealed: Counter, display: Counter) -> bool:
    melds_needed = 4 - _display_meld_count(display)

    if melds_needed < 0:
        return False

    # If all 4 melds are already displayed, concealed must form exactly 1 pair
    if melds_needed == 0:
        return (
            len(concealed) == 1
            and list(concealed.values())[0] == 2
        )

    # Try every possible pair from concealed tiles
    for tile, count in concealed.items():
        if count >= 2:
            remaining = concealed.copy()
            remaining[tile] -= 2
            if remaining[tile] == 0:
                del remaining[tile]
            frozen = frozenset(remaining.items())
            if _can_form_melds(frozen, melds_needed):
                return True

    return False


@lru_cache(maxsize=None)
def _can_form_melds(counter_frozen: frozenset, melds_needed: int) -> bool:
    """
    Recursively check whether exactly `melds_needed` melds (pong or chow)
    can be formed from the given tile counter.
    """
    counter = Counter(dict(counter_frozen))

    if melds_needed == 0:
        return len(counter) == 0

    if not counter:
        return False

    tile = min(counter)
    count = counter[tile]

    # Try pong (3 identical tiles)
    if count >= 3:
        new = counter.copy()
        new[tile] -= 3
        if new[tile] == 0:
            del new[tile]
        if _can_form_melds(frozenset(new.items()), melds_needed - 1):
            return True

    # Try chow (3 consecutive suit tiles)
    parts = tile.split("_")
    if len(parts) == 2 and parts[0].isdigit():
        num  = int(parts[0])
        suit = parts[1]
        if suit in SUITS and num <= 7:
            t2 = f"{num+1}_{suit}"
            t3 = f"{num+2}_{suit}"
            if counter.get(t2, 0) >= 1 and counter.get(t3, 0) >= 1:
                new = counter.copy()
                for t in (tile, t2, t3):
                    new[t] -= 1
                    if new[t] == 0:
                        del new[t]
                if _can_form_melds(frozenset(new.items()), melds_needed - 1):
                    return True

    return False


# ------------------------------------------------------------------ #
#  Special hand checks
# ------------------------------------------------------------------ #

def is_thirteen_wonders(concealed: Counter) -> bool:
    """
    十三幺 – one each of the 13 terminals/honors + exactly one duplicate.
    Must be entirely in concealed (no display melds allowed).
    """
    required = set()
    for suit in SUITS:
        required.add(f"1_{suit}")
        required.add(f"9_{suit}")
    for d in DRAGONS:
        required.add(d)
    for w in WINDS:
        required.add(w)

    if not required.issubset(concealed.keys()):
        return False

    pair_count = sum(1 for t in required if concealed[t] >= 2)
    return pair_count == 1 and sum(concealed.values()) == 14
