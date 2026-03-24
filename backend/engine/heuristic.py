"""
Singapore Mahjong – Discard Heuristic
======================================
Scores every tile in the concealed hand and returns the one to discard.

Strategy (higher score = more likely to discard):

Suit tiles
  • Off-suit when flush is viable (≥8 tiles in one suit)  : +60
  • Isolated (no adjacent tiles), single copy             : +50
  • Terminal (1 or 9), no adjacent tiles                  : +10 extra
  • Each adjacent neighbor in hand                        : -15 (connectivity bonus)
  • Isolated pair (no neighbors)                          : -10 (pong potential)

Honor tiles  (winds / dragons — can only form pong, never chow)
  • Single isolated honor                                 : +100
  • Pair (potential pong)                                 : +30
  • Triple / existing pong                                : 0   (keep)

Display tiles are excluded — they are already committed melds.
"""

from collections import Counter
from backend.representation.all_tiles import SUITS, WINDS, DRAGONS, ALL_TILES

HONORS = set(WINDS + DRAGONS)


# ------------------------------------------------------------------ #
#  Internal helpers
# ------------------------------------------------------------------ #

def _suit_of(tile: str) -> str | None:
    parts = tile.split("_")
    if len(parts) == 2 and parts[1] in SUITS:
        return parts[1]
    return None


def _neighbor_count(tile: str, hand_set: set[str]) -> int:
    """Number of tiles in hand_set that are 1 or 2 steps away (same suit)."""
    parts = tile.split("_")
    if len(parts) != 2 or not parts[0].isdigit():
        return 0
    num, suit = int(parts[0]), parts[1]
    return sum(
        1 for delta in (-2, -1, 1, 2)
        if f"{num + delta}_{suit}" in hand_set
    )


# ------------------------------------------------------------------ #
#  Public API
# ------------------------------------------------------------------ #

def best_discard(hand_obj: dict) -> str:
    """
    Return the tile name that should be discarded from hand_obj["concealed"].

    hand_obj must have at least a "concealed" key (Counter of tile → count).
    "display" is ignored (already committed).
    """
    concealed: Counter = hand_obj["concealed"]

    tiles     = [t for t, c in concealed.items() for _ in range(c)]
    hand_set  = set(tiles)
    unique    = list(concealed.keys())

    if not unique:
        raise ValueError("Concealed hand is empty.")

    # ── Determine flush viability ──────────────────────────────────
    suit_counts = {s: sum(1 for t in tiles if _suit_of(t) == s) for s in SUITS}
    dominant    = max(suit_counts, key=suit_counts.get)
    flush_viable = suit_counts[dominant] >= 8

    # ── Score each unique tile ─────────────────────────────────────
    scores: dict[str, float] = {}

    for tile in unique:
        count = concealed[tile]
        score = 0.0

        if tile in HONORS:
            if count == 1:
                score = 100.0          # isolated honor → discard first
            elif count == 2:
                score = 30.0           # pair → might pong, keep if possible
            else:
                score = 0.0            # pong/kong in hand → definitely keep

        else:
            suit = _suit_of(tile)
            num  = int(tile.split("_")[0])
            adj  = _neighbor_count(tile, hand_set)

            if flush_viable and suit != dominant:
                score += 60.0          # wrong suit for the flush we're building

            if adj == 0 and count == 1:
                score += 50.0          # completely isolated single tile
            elif adj == 0 and count == 2:
                score -= 10.0          # isolated pair → pong potential
            else:
                score -= adj * 15.0    # connected tile → keep

            if num in (1, 9):
                score += 10.0          # terminals are less flexible

        scores[tile] = score

    # Break ties by ALL_TILES order (deterministic)
    return max(scores, key=lambda t: (scores[t], ALL_TILES.index(t)))
