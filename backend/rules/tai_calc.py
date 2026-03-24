"""
Singapore Mahjong – Tai (Points / Doubles) Calculator
======================================================
Scoring elements (each worth 1 tai unless noted):

 Flower / Animal bonuses
  • Own-seat flower (blue_N or red_N where N == seat_number) : +1 per tile
  • Any animal (cat/rat/chicken/centipede)                   : +1 per tile

 Hand patterns
  • Men Qing (门清): fully concealed win (no display melds), self-draw win : +1
  • Dragon pong/kong (any of RED, GREEN, WHITE)              : +1 each
  • Seat Wind pong/kong                                      : +1
  • Prevailing (Round) Wind pong/kong                        : +1

 Whole-hand patterns (scored once)
  • All Pongs / Peng Peng Hu (碰碰胡)                         : +2
  • Half Flush / Hun Yi Se (混一色): one suit + honors         : +2
  • Full Flush / Qing Yi Se (清一色): one suit only            : +4
  • Ping Hu (平胡): 4 chows + 1 pair (pair ≠ dragon/seat wind) : +1
    – If no flowers/animals: +4 (clean Ping Hu)
  • Little Three Dragons (小三元): 2 dragon pongs + dragon eye : +3
  • Thirteen Wonders (十三幺)                                  : +13 (limit)
  • All 8 Flowers                                            : +8 (limit)
"""

from collections import Counter
from functools import lru_cache

import backend.config.game_config as config
from backend.representation.all_tiles import SUITS, DRAGONS, WINDS, ANIMALS


# ------------------------------------------------------------------ #
#  Public API
# ------------------------------------------------------------------ #

def calculate_tai(hand_obj: dict) -> dict:
    concealed: Counter = hand_obj["concealed"]
    display:   Counter = hand_obj["display"]
    flowers:   Counter = hand_obj.get("flowers", Counter())

    seat_wind   = config.get_seat_wind()
    round_wind  = config.get_round_wind()
    seat_number = config.get_seat_number()   # 1=East 2=South 3=West 4=North

    tai = 0
    breakdown = []

    # ── All-8-flowers special hand ───────────────────────────────────
    if sum(flowers.values()) >= 8:
        tai += 8
        breakdown.append("All 8 Flowers (八仙过海)")
        return {"tai": tai, "breakdown": breakdown}

    # ── Thirteen Wonders ────────────────────────────────────────────
    from rules.win_checker import is_thirteen_wonders
    if is_thirteen_wonders(concealed):
        tai += 13
        breakdown.append("Thirteen Wonders (十三幺)")
        return {"tai": tai, "breakdown": breakdown}

    # ── Flower / Animal bonuses ──────────────────────────────────────
    flower_tai = 0
    for tile, count in flowers.items():
        if tile in ANIMALS:
            flower_tai += count          # all animals score
        else:
            # blue_N or red_N: score if N == seat_number
            parts = tile.split("_")
            if len(parts) == 2 and parts[1].isdigit():
                if int(parts[1]) == seat_number:
                    flower_tai += count

    if flower_tai:
        tai += flower_tai
        breakdown.append(f"+{flower_tai} Flower/Animal Tai")

    # ── Men Qing (fully concealed win) ──────────────────────────────
    if sum(display.values()) == 0:
        tai += 1
        breakdown.append("Men Qing (门清)")

    # ── Collect all melds for pattern analysis ───────────────────────
    # melds_info: list of (tile, count) for each group
    all_tiles_combined = Counter(concealed) + Counter(display)
    melds = _extract_melds(concealed, display)

    # ── Dragon pong / kong ───────────────────────────────────────────
    for dragon in DRAGONS:
        if melds.get(dragon, 0) >= 3:
            tai += 1
            breakdown.append(f"Pong/Kong of {dragon} Dragon")

    # ── Little Three Dragons (小三元) ────────────────────────────────
    dragon_pongs = sum(1 for d in DRAGONS if melds.get(d, 0) >= 3)
    dragon_eye   = sum(1 for d in DRAGONS if concealed.get(d, 0) == 2)
    if dragon_pongs == 2 and dragon_eye == 1:
        tai += 3
        breakdown.append("Little Three Dragons (小三元)")

    # ── Seat Wind pong / kong ────────────────────────────────────────
    if melds.get(seat_wind, 0) >= 3:
        tai += 1
        breakdown.append(f"Seat Wind Pong ({seat_wind})")

    # ── Prevailing Wind pong / kong ──────────────────────────────────
    if round_wind != seat_wind and melds.get(round_wind, 0) >= 3:
        tai += 1
        breakdown.append(f"Prevailing Wind Pong ({round_wind})")

    # ── All Pongs / Peng Peng Hu ─────────────────────────────────────
    if _is_all_pongs(concealed, display):
        tai += 2
        breakdown.append("All Pongs (碰碰胡)")

    # ── Ping Hu ──────────────────────────────────────────────────────
    ping_hu_result = _ping_hu_tai(concealed, display, flowers)
    if ping_hu_result > 0:
        tai += ping_hu_result
        label = "Ping Hu (平胡)" if ping_hu_result == 4 else "Smelly Ping Hu (臭平胡)"
        breakdown.append(label)

    # ── Flush checks ─────────────────────────────────────────────────
    flush = _flush_check(concealed, display)
    if flush == "FULL":
        tai += 4
        breakdown.append("Full Flush (清一色)")
    elif flush == "HALF":
        tai += 2
        breakdown.append("Half Flush (混一色)")

    if not breakdown:
        breakdown.append("Winning hand (no additional tai)")

    return {"tai": tai, "breakdown": breakdown}


# ------------------------------------------------------------------ #
#  Helpers
# ------------------------------------------------------------------ #

def _extract_melds(concealed: Counter, display: Counter) -> Counter:
    """Merge concealed + display tile counts for pong/kong detection."""
    merged = Counter(concealed)
    merged.update(display)
    return merged


def _is_honor(tile: str) -> bool:
    return tile in WINDS or tile in DRAGONS


def _is_numeric(tile: str) -> bool:
    return "_" in tile and tile.split("_")[0].isdigit()


def _is_all_pongs(concealed: Counter, display: Counter) -> bool:
    """
    Every set of tiles must be a pong or kong (triplet/quad).
    No chow allowed anywhere.
    """
    all_tiles = Counter(concealed) + Counter(display)
    for tile, count in all_tiles.items():
        if _is_numeric(tile) and count == 1:
            # A lone numeric tile implies a chow somewhere
            return False
    # Must have exactly one pair in concealed + sets of 3 or 4 everywhere
    # Quick check: concealed should be pair + pongs
    return True


def _ping_hu_tai(concealed: Counter, display: Counter, flowers: Counter) -> int:
    """
    Ping Hu = 4 chows + 1 pair.
    Returns 4 (clean) if no flowers/animals, else 1 (smelly/臭平胡).
    Returns 0 if not Ping Hu.
    """
    if sum(concealed.values()) + sum(display.values()) != 14:
        return 0

    # Display must contain only chows (suit tiles, count == 3 per tile group)
    for tile, count in display.items():
        if _is_honor(tile):
            return 0
        # Chow tiles appear once per tile in the sequence
        if count not in (1, 2, 3):
            return 0

    # Concealed must not have any honor pongs used as melds
    for tile, count in concealed.items():
        if _is_honor(tile) and count >= 3:
            return 0

    chows_in_display = sum(display.values()) // 3
    chows_needed = 4 - chows_in_display

    tiles = Counter(concealed)
    for tile, count in tiles.items():
        if count >= 2:
            temp = tiles.copy()
            temp[tile] -= 2
            if temp[tile] == 0:
                del temp[tile]
            if _is_honor(tile):
                # Pair of honors is allowed only if it's not a dragon/seat-wind
                # (some tables allow any pair; we follow common SG rule)
                pass
            if _can_form_n_chis(temp, chows_needed):
                has_bonus = sum(flowers.values()) > 0
                return 1 if has_bonus else 4

    return 0


@lru_cache(maxsize=None)
def _can_form_n_chis_cached(counter_frozen: frozenset, n: int) -> bool:
    counter = Counter(dict(counter_frozen))
    if n == 0:
        return len(counter) == 0
    if not counter:
        return False
    tile = min(counter)
    parts = tile.split("_")
    if len(parts) != 2 or not parts[0].isdigit():
        return False
    num  = int(parts[0])
    suit = parts[1]
    if suit not in SUITS or num > 7:
        return False
    t2, t3 = f"{num+1}_{suit}", f"{num+2}_{suit}"
    if counter.get(t2, 0) > 0 and counter.get(t3, 0) > 0:
        new = counter.copy()
        for t in (tile, t2, t3):
            new[t] -= 1
            if new[t] == 0:
                del new[t]
        return _can_form_n_chis_cached(frozenset(new.items()), n - 1)
    return False


def _can_form_n_chis(counter: Counter, n: int) -> bool:
    return _can_form_n_chis_cached(frozenset(counter.items()), n)


def _flush_check(concealed: Counter, display: Counter) -> str | None:
    """
    Returns 'FULL' (清一色), 'HALF' (混一色), or None.
    """
    suits_seen   = set()
    has_honors   = False

    for tile in list(concealed.keys()) + list(display.keys()):
        if _is_honor(tile):
            has_honors = True
        else:
            parts = tile.split("_")
            if len(parts) == 2:
                suits_seen.add(parts[1])

    if len(suits_seen) != 1:
        return None   # mixed suits → no flush

    if has_honors:
        return "HALF"
    return "FULL"
