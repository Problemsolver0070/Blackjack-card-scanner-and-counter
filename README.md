# Blackjack Card Scanner and Counter

A Linux application that performs real-time screen analysis to detect playing cards and calculate optimal bet sizing for blackjack games using full deck composition tracking.

## Overview

This software monitors your screen in real-time, detects blackjack cards being played, and provides precise card counting metrics including:
- **Strategy Advisor**: Tells you the optimal action (Hit/Stand/Double/Split/Surrender) with composition-dependent deviations
- **Optimal Bet Size**: Exact bet amount in units using Kelly Criterion
- **Player Advantage**: Calculated edge based on exact deck composition
- **Dealer Bust Probability**: Real-time chance of dealer busting based on composition
- **Full Composition Tracking**: Monitors every single card remaining in the shoe
- **Shoe Penetration**: Percentage of cards dealt from the shoe

## Features

- 🎴 Real-time card detection using computer vision (OpenCV)
- 🎯 **Strategy Advisor**: Basic strategy + composition-dependent deviations
- 🧮 Full deck composition tracking (not simplified counting systems)
- 📊 Exact player advantage calculation using Effect of Removal (EOR)
- 💰 Kelly Criterion optimal bet sizing in units
- 🎲 Dealer bust probability based on current composition
- 🖥️ Always-on-top GUI display
- 📈 Key card composition display (5s, 6s, 10s, Aces)
- 🃏 Optimized for 8-deck shoes with ~50% penetration
- 🔄 Easy reset between shoes
- ⚡ Low CPU usage and efficient screen capture

## Quick Start

### Installation

```bash
# Run the setup script
chmod +x setup.sh
./setup.sh
```

### Usage

```bash
# Launch the application
python3 blackjack_counter.py
```

1. Open your online blackjack game (optimized for 8-deck shoes)
2. Click "Start Scanning" in the counter window
3. Play as normal - the count updates automatically
4. Click "New Shoe" when a new shoe begins

## System Requirements

- Linux (X11 display server)
- Python 3.7+
- pip3

## Documentation

- [Installation Guide](INSTALL.md) - Detailed setup instructions
- [Usage Guide](USAGE.md) - How to use the application effectively

## How It Works

### Full Deck Composition Tracking

Unlike simplified counting systems (Hi-Lo, KO, etc.), this application tracks the **exact composition** of every card remaining in the shoe:

- Maintains count of all 13 ranks (2-A) across all decks
- Calculates player advantage using Effect of Removal (EOR) values
- Each card rank has a specific impact on player edge
- More accurate than traditional counting systems

**Configuration**: Optimized for 8-deck shoes (416 cards total), the standard for most online casinos. Online casinos typically use ~50% penetration (208 cards dealt before shuffle), which provides sufficient data for accurate advantage calculation while limiting counter effectiveness.

### Effect of Removal (EOR)

The system uses EOR values to determine how each card affects player advantage:

| Card | EOR Impact |
|------|------------|
| 5 | +0.67% (most beneficial to remove) |
| 4 | +0.52% |
| 6 | +0.45% |
| 2, 3 | +0.40-0.43% |
| 7 | +0.30% |
| 8 | ±0.01% (neutral) |
| 9 | -0.19% |
| 10, J, Q, K | -0.51% (hurts when removed) |
| A | -0.59% (most harmful to remove) |

### Kelly Criterion Bet Sizing

Optimal bet = (Player Edge / Variance) × Bankroll

- Uses 1/4 Kelly for conservative risk management
- Automatically calculates bet size in units
- Considers current advantage and bankroll
- Maximum bet capped at 10% of total bankroll

### Dealer Bust Probability

The system calculates the real-time probability of the dealer busting based on current deck composition:

**How it works**:
- Starts with base bust probabilities for each possible dealer upcard
- Adjusts based on remaining high cards (10s, face cards) and low cards (2-6)
- More 10-value cards remaining = higher dealer bust probability (good for player)
- More low cards remaining = lower dealer bust probability (bad for player)

**Base dealer bust rates** (neutral deck, S17 rules):
- Dealer showing 5 or 6: ~42% (worst for dealer)
- Dealer showing 2-4: ~35-40%
- Dealer showing 7-9: ~23-26%
- Dealer showing 10: ~21%
- Dealer showing Ace: ~12%

The displayed bust probability is a weighted average across all possible dealer upcards, adjusted for the current composition. When the deck is rich in 10s, this percentage increases significantly.

### Strategy Advisor

The application includes a complete strategy engine that tells you the optimal play for any situation:

**Basic Strategy Implementation**:
- Complete basic strategy for S17 (dealer stands on soft 17)
- Handles hard totals, soft totals, and pairs
- Includes surrender when applicable
- Considers doubling restrictions

**Composition-Dependent Deviations**:
When the deck composition gives you an edge, the system recommends deviating from basic strategy:

| Situation | Basic Strategy | High Count Deviation | When |
|-----------|----------------|---------------------|------|
| 16 vs 10 | Hit/Surrender | **STAND** | Advantage ≥ +0.5% |
| 15 vs 10 | Surrender | **STAND** | Advantage ≥ +1.0% |
| 12 vs 2 | Hit | **STAND** | Advantage ≥ +1.0% |
| 12 vs 3 | Hit | **STAND** | Advantage ≥ +0.8% |
| 10 vs 10 | Hit | **DOUBLE** | Advantage ≥ +1.5% |
| 10 vs A | Hit | **DOUBLE** | Advantage ≥ +1.5% |
| 9 vs 2 | Hit | **DOUBLE** | Advantage ≥ +0.5% |

**How to use**:
1. Enter your hand (e.g., "10,6" or "A,5")
2. Enter dealer's upcard (e.g., "10" or "A")
3. Click "Get Action"
4. The app shows the optimal play with reasoning

Deviations are highlighted in **deep orange** to alert you when the composition warrants a non-standard play.

### Technology Stack

- **OpenCV**: Computer vision for card detection
- **mss**: Efficient cross-platform screen capture
- **NumPy**: Numerical computations
- **Tkinter**: GUI interface
- **Python Threading**: Non-blocking screen analysis

## Legal & Ethical Notice

**Important**:
- Card counting is a legal strategy in most jurisdictions when done mentally
- Casinos may refuse service to known card counters
- Use of electronic devices for counting may be prohibited by casino terms
- This software is intended for **educational purposes** only
- Users are responsible for compliance with local laws and casino policies
- Always gamble responsibly

## Current Status

This is a functional implementation with the following capabilities:

✅ Screen capture and monitoring
✅ Full deck composition tracking (all 13 ranks)
✅ **Strategy Advisor with composition-dependent deviations**
✅ Exact player advantage calculation using EOR
✅ Kelly Criterion optimal bet sizing
✅ Dealer bust probability (composition-adjusted)
✅ GUI with live updates showing bet in units
✅ Key card composition display

⚠️ **Note**: Card detection accuracy depends on screen quality, card visibility, and casino interface. The current implementation uses contour detection - for production use, consider implementing template matching or machine learning models for your specific casino.

## Contributing

Contributions are welcome! Areas for improvement:
- Enhanced card detection with ML models or OCR
- Template matching for specific online casinos
- Multi-monitor support configuration
- Region selection for targeted scanning
- Adjustable Kelly fraction and risk parameters
- Export statistics and session tracking
- Support for different rule variations (S17, H17, DAS, etc.)

## License

This project is provided for educational purposes. Users must comply with all applicable laws and regulations.

## Disclaimer

This software is provided "as is" without warranty of any kind. The authors are not responsible for any losses incurred through use of this software. Gambling involves risk - never bet more than you can afford to lose.
