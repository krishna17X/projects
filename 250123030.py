# player_template.py
"""
Simplified PokerBot – Player Template

You ONLY need to modify the `decide_action` function below.

The tournament engine (master.py) will:
  - Call this script once per round.
  - Send you a single JSON object on stdin describing the game state.
  - Expect a JSON object on stdout: {"action": "FOLD" or "CALL" or "RAISE"}

Your job:
  - Read the state.
  - Decide whether to FOLD / CALL / RAISE using a *quantitative* strategy.
  - Output the action as JSON.

You are free to:
  - Add helper functions.
  - Use probability / EV calculations.
  - Use opponent statistics for adaptive strategies.
  - As long as you keep the I/O format the same.
"""

import json
import sys
from typing import List, Tuple

# -------------------------
# 1. Basic card utilities
# -------------------------

# Ranks from lowest to highest. T = 10, J = Jack, Q = Queen, K = King, A = Ace.
RANKS = "23456789TJQKA"
# Map rank character -> numeric value (2..14)
RANK_VALUE = {r: i + 2 for i, r in enumerate(RANKS)}  # 2..14 (A=14)


def parse_card(card_str: str) -> Tuple[int, str]:
    """
    Convert a string like "AH" or "7D" into (rank_value, suit).

    Example:
        "AH" -> (14, 'H')
        "7D" -> (7, 'D')

    card_str[0]: rank in "23456789TJQKA"
    card_str[1]: suit in "CDHS"  (Clubs, Diamonds, Hearts, Spades)
    """
    return RANK_VALUE[card_str[0]], card_str[1]


def is_straight_3(rank_values: List[int]) -> Tuple[bool, int]:
    """
    Check if 3 cards form a straight under our custom rules.

    Rules:
      - 3 cards are a straight if they are in sequence.
      - A can be:
          * LOW in A-2-3  (treated as the LOWEST straight)
          * HIGH in Q-K-A (treated as the highest normal case)
      - Return:
          (is_straight: bool, high_card_value_for_straight: int)

    Examples:
      [2, 3, 4]    -> (True, 4)
      [12, 13, 14] -> Q-K-A -> (True, 14)
      [14, 2, 3]   -> A-2-3 -> (True, 3)  (lowest straight)
    """
    r = sorted(rank_values)

    # Normal consecutive: x, x+1, x+2
    if r[0] + 1 == r[1] and r[1] + 1 == r[2]:
        return True, r[2]

    # A-2-3 special: {14,2,3} -> treat as straight with high=3
    if set(r) == {14, 2, 3}:
        return True, 3

    return False, 0


# --------------------------------------
# 2. Hand category evaluation (3 cards)
# --------------------------------------

"""
Hand is always: your 2 hole cards + 1 community card = 3 cards.

We classify them into 6 categories (from weakest to strongest):

  0: HIGH CARD
  1: PAIR
  2: FLUSH
  3: STRAIGHT
  4: TRIPS  (Three of a kind)
  5: STRAIGHT FLUSH

And the *global ranking* is:

  STRAIGHT_FLUSH (5) > TRIPS (4) > STRAIGHT (3) > FLUSH (2) > PAIR (1) > HIGH_CARD (0)

This function only returns the category index 0..5,
not the tie-break details (you don't strictly need tie-breaks inside your bot).
"""


def hand_category(hole: List[str], table: str) -> int:
    """
    Compute the hand category for your 3-card hand.

    Input:
        hole  = ["AS", "TD"], etc. (your two private cards)
        table = "7H"           (community card)

    Returns:
        0..5 as defined above.
    """
    cards = hole + [table]
    rank_values, suits = zip(*[parse_card(c) for c in cards])
    flush = len(set(suits)) == 1  # True if all 3 suits are the same

    # Count how many times each rank appears
    counts = {}
    for v in rank_values:
        counts[v] = counts.get(v, 0) + 1

    straight, _ = is_straight_3(list(rank_values))

    if straight and flush:
        return 5  # Straight Flush
    if 3 in counts.values():
        return 4  # Trips
    if straight:
        return 3  # Straight
    if flush:
        return 2  # Flush
    if 2 in counts.values():
        return 1  # Pair
    return 0      # High Card


# ----------------------------------------
# 3. Scoring summary (for your reference)
# ----------------------------------------
"""
IMPORTANT: these are the points awarded PER ROUND
depending on the actions and showdown result.

Notation:
  - "Showdown" means nobody folded: cards are compared.
  - result = which player wins the hand, not part of your code directly.

Fold scenarios (no showdown):
  P1: FOLD, P2: FOLD  ->  (0, 0)
  P1: FOLD, P2: CALL  ->  (-1, +2)
  P1: FOLD, P2: RAISE ->  (-1, +3)
  P1: CALL, P2: FOLD  ->  (+2, -1)
  P1: RAISE, P2: FOLD ->  (+3, -1)

Showdown scenarios (someone has better hand):
  Both CALL:
    - P1 wins: (+2, -2)
    - P2 wins: (-2, +2)

  P1 RAISE, P2 CALL:
    - P1 wins: (+3, -2)
    - P2 wins: (-3, +2)

  P1 CALL, P2 RAISE:
    - P1 wins: (+2, -3)
    - P2 wins: (-2, +3)

  P1 RAISE, P2 RAISE (High-Risk round):
    - P1 wins: (+3, -3)
    - P2 wins: (-3, +3)

Any showdown where hands are *exactly* identical:
  -> (0, 0)

Your bot does NOT see the opponent's current action,
but it CAN see opponent action frequencies over previous rounds
(via `opponent_stats`).
Use this to think in terms of EXPECTED VALUE (EV), not just raw hand strength.
"""
import random
from itertools import combinations

# Fuction to generate full deck

def helper_function_1():
    suits = ["C", "D", "H", "S"]
    return [r + s for r in RANKS for s in suits]

# Function to estimate win probability
def helper_function_2(hole, table, simulations=450):
    deck = helper_function_1()

    known_cards = set(hole + [table])
    remaining = [c for c in deck if c not in known_cards]

    win = lose = tie = 0
    my_category = hand_category(hole, table)

    for i in range(simulations):
        opp_hole = random.sample(remaining, 2)
        opp_category = hand_category(opp_hole, table)

        if my_category > opp_category:
            win += 1
        elif my_category < opp_category:
            lose += 1
        else:
            tie += 1

    total = win + lose + tie
    return {
        "win": win / total,
        "lose": lose / total,
        "tie": tie / total
    }
# -----------------------------------
# 4. Main strategy function to edit
# -----------------------------------

def decide_action(state: dict) -> str:

    # 1) get state

    hole = state["your_hole"]
    table = state["table_card"]
    opp = state.get("opponent_stats") or {"fold": 0, "call": 0, "raise": 0}

    
    # 2) Hand category
   
    category = hand_category(hole, table)

    
    # 3) Opponent tendencies
    
    total_opp_actions = opp["fold"] + opp["call"] + opp["raise"]

    if total_opp_actions == 0:
        opp_fold_rate = 1 / 3
        opp_call_rate = 1 / 3
        opp_raise_rate = 1 / 3
    else:
        opp_fold_rate = opp["fold"] / total_opp_actions
        opp_call_rate = opp["call"] / total_opp_actions
        opp_raise_rate = opp["raise"] / total_opp_actions

    
    # 4) Win probability
    
    probs = helper_function_2(hole, table)
    p_win = probs["win"]
    p_lose = probs["lose"]
    p_tie = probs["tie"]

    
    # 5) Expected Value (EV)
   

    # FOLD
    EV_FOLD = opp_fold_rate * 0 + (1 - opp_fold_rate) * (-1)

    # CALL
    EV_CALL = (
        opp_fold_rate * 2 +
        opp_call_rate * (p_win * 2 + p_lose * (-2)) +
        opp_raise_rate * (p_win * 2 + p_lose * (-3))
    )

    # RAISE
    EV_RAISE = (
        opp_fold_rate * 3 +
        opp_call_rate * (p_win * 3 + p_lose * (-2)) +
        opp_raise_rate * (p_win * 3 + p_lose * (-3))
    )

    # Very weak hand + very aggressive opponent → fold
    if category == 0 and opp_raise_rate > 0.60:
        return "FOLD"

    # ------------------------------------------------
    # other wise TRUST EV 
    # ------------------------------------------------
    if EV_RAISE > EV_CALL and EV_RAISE > EV_FOLD:
        return "RAISE"
    elif EV_CALL > EV_FOLD:
        return "CALL"
    else:
        return "FOLD"


# -----------------------------
# 5. I/O glue (do not touch)
# -----------------------------

def main():
    """
    DO NOT modify this unless you know what you're doing.

    It:
      - Reads one JSON object from stdin.
      - Calls decide_action(state).
      - Writes {"action": "..."} as JSON to stdout.
    """
    raw = sys.stdin.read().strip()
    try:
        state = json.loads(raw) if raw else {}
    except Exception:
        state = {}

    action = decide_action(state)

    # Safety check: default to CALL if something invalid is returned
    if action not in {"FOLD", "CALL", "RAISE"}:
        action = "CALL"

    sys.stdout.write(json.dumps({"action": action}))


if __name__ == "__main__":
    main()
