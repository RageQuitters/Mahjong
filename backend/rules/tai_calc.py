import config.game_config as config
from collections import Counter

SUITS = ["DOT", "CHAR", "BAM"]
DRAGONS = ["GREEN", "RED", "WHITE"]
WINDS = ["EAST", "SOUTH", "WEST", "NORTH"]


def calculate_tai(hand_obj):
    concealed = hand_obj["concealed"]
    display = hand_obj["display"]
    flowers = hand_obj["flowers"]

    seat_wind = config.get_seat_wind()
    round_wind = config.get_round_wind()
    seat_number = config.get_seat_number()

    tai = 0
    breakdown = []

    # Base win tai
    tai += 0
    breakdown.append("Winning hand")

    # -------------------------
    # Flower tai (seat-based)
    # -------------------------

    flower_tai = 0

    for flower, count in flowers.items():
        parts = flower.split("_")
        if len(parts) != 2:
            flower_tai += count
            continue

        color, num = parts
        if not num.isdigit():
            continue

        if int(num) == seat_number:
            flower_tai += count

    if flower_tai > 0:
        tai += flower_tai
        breakdown.append(f"{flower_tai} Seat Flower/Animal Tai")

    # Men Qing
    if sum(display.values()) == 0:
        tai += 1
        breakdown.append("Men Qing (门清)")

    # Special hands
    if is_thirteen_wonders(concealed):
        tai += 13
        breakdown.append("Thirteen Wonders (十三幺)")
        return {"tai": tai, "breakdown": breakdown}

    # Meld analysis
    melds = get_all_melds(concealed, display)

    # Dragon pongs
    for d in DRAGONS:
        tile = f"{d}"
        if melds.get(tile, 0) >= 3:
            tai += 1
            breakdown.append(f"Pong of {d} Dragon")

    # Seat wind pong
    seat_tile = f"{seat_wind}_WIND"
    if melds.get(seat_tile, 0) >= 3:
        tai += 1
        breakdown.append("Seat Wind Pong")

    # Round wind pong
    round_tile = f"{round_wind}_WIND"
    if melds.get(round_tile, 0) >= 3:
        tai += 1
        breakdown.append("Round Wind Pong")

    # All Pongs (Peng Peng Hu)
    if is_all_pongs(concealed, display):
        tai += 2
        breakdown.append("All Pongs (碰碰胡)")

    # Ping Hu
    if is_ping_hu(concealed, display, flowers):
        tai += 4 if sum(flowers.values()) == 0 else 1
        breakdown.append("Ping Hu (平胡)") if sum(flowers.values()) == 0 else breakdown.append("Chou Ping Hu (臭平胡)")

    # Flushes
    flush_type = flush_check(concealed, display)
    if flush_type == "FULL":
        tai += 4
        breakdown.append("Full Flush (清一色)")
    elif flush_type == "HALF":
        tai += 2
        breakdown.append("Half Flush (混一色)")

    return {"tai": tai, "breakdown": breakdown}


# -------------------------
# Helper functions
# -------------------------

def get_all_melds(concealed, display):
    melds = Counter()
    melds.update(concealed)
    melds.update(display)
    return melds

def parse_tile(tile):
    parts = tile.split("_")
    if len(parts) != 2:
        return None, None
    try:
        return int(parts[0]), parts[1]
    except ValueError:
        return None, parts[1]


def is_ping_hu(concealed: Counter, display: Counter, flowers: Counter) -> bool:
    """
    Check for Ping Hu:
    - 4 sequences (Chis) + 1 pair
    - Display can contain only sequences
    - Pair from concealed only
    - No honors in sequences
    - Allow flowers (chou pinghu also valid here)
    """

    # 2️⃣ Total tiles must be 14
    if sum(concealed.values()) + sum(display.values()) != 14:
        return False
    
    # Check that display contains only sequences (chis)
    for tile, count in display.items():
        if count != 3:
            return False
        num, suit = parse_tile(tile)
        if suit not in SUITS:
            return False  # display contains honor pong, invalid

    # Check that concealed has no honor pongs
    for tile, count in concealed.items():
        if is_honor(tile) and count >= 3:
            return False

    # 3️⃣ Count how many sequences are already in display
    num_display_chis = sum(display.values()) // 3
    sequences_needed = 4 - num_display_chis

    # 4️⃣ Try every possible pair from concealed
    tiles_counter = Counter(concealed)
    for tile, count in tiles_counter.items():
        if count >= 2:
            temp_counter = tiles_counter.copy()
            temp_counter[tile] -= 2
            if temp_counter[tile] == 0:
                del temp_counter[tile]

            # Check if remaining tiles can form the remaining sequences
            if can_form_n_chis(temp_counter, sequences_needed):
                return True

    return False

def can_form_n_chis(counter: Counter, n: int) -> bool:
    """
    Recursively check if exactly n sequences (Chis) can be formed
    Honors are not allowed in sequences
    """
    if n == 0:
        return len(counter) == 0  # all tiles used
    if not counter:
        return False

    tile = min(counter)
    num, suit = parse_tile(tile)
    if num is None or suit not in SUITS:
        return False

    t2 = f"{num+1}_{suit}"
    t3 = f"{num+2}_{suit}"
    if counter.get(t2, 0) > 0 and counter.get(t3, 0) > 0:
        new_counter = counter.copy()
        for t in [tile, t2, t3]:
            new_counter[t] -= 1
            if new_counter[t] == 0:
                del new_counter[t]
        return can_form_n_chis(new_counter, n-1)

    return False


def is_all_pongs(concealed, display):
    # No sequences possible if any numeric tile appears only once
    for tile, count in concealed.items():
        if is_numeric(tile) and count == 1:
            return False
    return True


def flush_check(concealed, display):
    suits = set()

    for tile in list(concealed.keys()) + list(display.keys()):
        parts = tile.split("_")
        if len(parts) == 2 and parts[1] in SUITS:
            suits.add(parts[1])
        elif is_honor(tile):
            continue
        else:
            return None

    if len(suits) == 1:
        if any(is_honor(t) for t in concealed) or any(is_honor(t) for t in display):
            return "HALF"
        return "FULL"

    return None


def is_numeric(tile):
    return tile.split("_")[0].isdigit()


def is_honor(tile):
    return any(d in tile for d in DRAGONS) or any(w in tile for w in WINDS)


def is_thirteen_wonders(counter):
    required = set()

    for suit in SUITS:
        required.add(f"1_{suit}")
        required.add(f"9_{suit}")

    for d in DRAGONS:
        required.add(f"{d}")

    for w in WINDS:
        required.add(f"{w}")

    if not required.issubset(counter.keys()):
        return False

    pair_count = sum(1 for t in required if counter[t] == 2)
    return pair_count == 1
