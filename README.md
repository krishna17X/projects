# Quantitative PokerBot 🃏📊

A simplified Python-based Poker bot that utilizes quantitative analysis, probability estimation, and Expected Value (EV) calculations to make optimal gameplay decisions.

## 🧠 Quantitative Approach & Strategy

This bot makes decisions purely based on mathematical logic rather than simple heuristics. The core logic relies on two main pillars:

### 1. Probability Estimation (Monte Carlo)
* We use a Monte Carlo Approximation to find the probability of winning.
* The estimated probability value is kept as close as possible to the actual value so it does not negatively affect the bot's decision-making.
* We use a straightforward category logic to evaluate hands; if our hand category outranks the opponent's simulated hand, it counts as a win, while a lower category counts as a loss.
* Receiving the exact same hand category is counted as a tie, completing our probability metric.

### 2. Expected Value (EV) Strategy
* We calculate the Expected Value (EV) for all three possible actions: fold, call, and raise.
* The bot considers the opponent's past tendencies to call, fold, or raise, and incorporates these probabilities into the EV calculation.
* The bot chooses the action that yields the highest calculated EV, ensuring every move is quantitatively sound.
* This means we not only look at the current hand's win probability, but we also adapt to the decision-making and performance of the opponent over previous rounds.

## 🛡️ Risk Modeling & Assumptions

* **Aggression Mitigation:** If the opponent is acting too aggressively and we hold a weak hand, we force the bot to fold, minimizing the risk of losing large points.
* **Loss Control:** We ensure that in cases of weak hands facing heavy raises, the point loss is kept to a minimum.
* **Assumptions:** We assume that ignoring tie-breakers within the same hand category during the Monte Carlo simulations will not cause a significant deviation from the true probability, and that the EV-driven decision will remain accurate regardless.

## 🚀 Getting Started
* The core logic is housed in the `decide_action` function.
* The bot reads standard game state JSON from `stdin` and outputs its action (FOLD, CALL, RAISE) to `stdout`.
