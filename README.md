# Blackjack Card Scanner and Counter

A Linux application that performs real-time screen analysis to detect playing cards and calculate bet sizing for blackjack using full deck composition tracking.

The software monitors a region of the screen, detects cards as they appear, and reports counting metrics: strategy advice (Hit/Stand/Double/Split/Surrender) with composition-dependent deviations, Kelly-based bet size in units, player advantage from exact deck composition, dealer bust probability, full composition tracking across all 13 ranks, and shoe penetration.

## Install

```bash
chmod +x setup.sh
./setup.sh
```

## Run

```bash
python3 blackjack_counter.py
```

The counter window stays on top. Click "Start Scanning" to begin analysis, and "New Shoe" to reset state when a new shoe starts. The default configuration assumes an 8-deck shoe.

## Requirements

- Linux with X11
- Python 3.7+
- pip3

## Additional documentation

- `INSTALL.md` - setup details
- `USAGE.md` - operating notes

## Full deck composition tracking

Rather than a reduced count like Hi-Lo or KO, the application tracks the exact count of every rank (2 through A) remaining in the shoe. Player advantage is computed from Effect of Removal (EOR) values, where each rank contributes a fixed delta to player edge per card removed. The defaults target 8-deck shoes (416 cards) with ~50% penetration (208 cards dealt before shuffle), which is typical for many online tables.

## Effect of Removal

EOR values used by the advantage calculation:

| Card | EOR Impact |
|------|------------|
| 5 | +0.67% |
| 4 | +0.52% |
| 6 | +0.45% |
| 2, 3 | +0.40 to +0.43% |
| 7 | +0.30% |
| 8 | ±0.01% |
| 9 | -0.19% |
| 10, J, Q, K | -0.51% |
| A | -0.59% |

## Kelly Criterion bet sizing

Bet size is computed as `(player_edge / variance) * bankroll`. The implementation uses 1/4 Kelly to dampen variance, expresses bet size in units, and caps any single bet at 10% of bankroll.

## Dealer bust probability

The dealer bust probability is computed from the current composition. Base rates per upcard under S17 are:

- Upcard 5 or 6: ~42%
- Upcard 2-4: ~35-40%
- Upcard 7-9: ~23-26%
- Upcard 10: ~21%
- Upcard A: ~12%

The displayed value is a weighted average over possible upcards, adjusted by the remaining counts of high cards (10-value) and low cards (2-6). A shoe rich in 10s raises the value; a shoe rich in low cards lowers it.

## Strategy advisor

For each decision, the engine computes Expected Value for each legal action against the current composition:

1. **EV(Stand)**: probability-weighted comparison of player total against dealer outcomes, using dealer-outcome distributions derived from the remaining cards.
2. **EV(Hit)**: sum over each remaining rank of `P(draw rank) * EV(resulting hand)`, where the resulting hand is evaluated by the same machinery (typically reducing to a stand EV after the draw).
3. **EV(Double)**: 2 * EV of a single drawn card with no further action.
4. The action with the maximum EV is returned.

Basic strategy is derived from an infinite-deck assumption. Because this engine recomputes from the actual remaining cards, it produces composition-dependent deviations automatically. Examples:

| Situation | Basic Strategy | Composition-Dependent Result |
|-----------|----------------|------------------------------|
| 16 vs 10 | Hit/Surrender | Stand when many small cards are gone |
| 12 vs 2 | Hit | Stand when shoe is rich in 10s |
| 10 vs 10 | Hit | Double when shoe is very rich in 10s |
| 9 vs 2 | Hit | Double when composition supports it |

To use it: enter your hand (e.g. `10,6` or `A,5`), enter the dealer upcard (e.g. `10` or `A`), and click "Get Action". Deviations from basic strategy are highlighted and the underlying EVs are shown, e.g. `Stand EV=0.156 > Hit EV=0.142 (Edge: +0.8%)`.

## Stack

- OpenCV for card detection
- mss for screen capture
- NumPy
- Tkinter for the GUI
- Python threading for non-blocking capture

## Legal and ethical notes

Card counting performed mentally is legal in most jurisdictions, but casinos may refuse service to known counters, and use of electronic aids may violate house rules or local law. This code is intended for educational use and analysis of recorded play. Users are responsible for complying with applicable law and the terms of any platform they interact with.

## Status

Implemented:

- Screen capture and monitoring
- Full composition tracking across all 13 ranks
- Strategy advisor with composition-dependent deviations
- Player advantage via EOR
- Kelly Criterion bet sizing
- Composition-adjusted dealer bust probability
- GUI with live updates and bet-in-units display
- Key card composition display (5s, 6s, 10s, Aces)

The current card detector uses contour detection, which is sensitive to screen quality and the table interface in use. For more robust detection, swap in template matching or a trained model tuned to your target interface.

## Contributing

Useful directions:

- Better card detection (template matching, ML, OCR)
- Per-interface templates
- Multi-monitor and region-of-interest selection
- Configurable Kelly fraction and risk caps
- Session export and statistics
- Rule variants (S17, H17, DAS, etc.)

## License

Provided for educational purposes. Users must comply with applicable law.

## Disclaimer

Provided "as is" without warranty. The authors are not responsible for any losses incurred. Gambling involves risk; do not bet more than you can afford to lose.
