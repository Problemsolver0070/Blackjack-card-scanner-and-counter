# Blackjack Card Scanner and Counter

A Linux application that performs real-time screen analysis to detect playing cards and calculate the true count for blackjack games using the Hi-Lo counting system.

## Overview

This software monitors your screen in real-time, detects blackjack cards being played, and provides live card counting metrics including:
- **True Count**: The main advantage indicator
- **Running Count**: Raw count of cards seen
- **Decks Remaining**: Estimated cards left in the shoe
- **Betting Recommendations**: Strategic advice based on the count

## Features

- 🎴 Real-time card detection using computer vision (OpenCV)
- 🧮 Hi-Lo card counting system implementation
- 📊 Live true count calculation
- 🖥️ Always-on-top GUI display
- 🎯 Betting strategy recommendations
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

1. Open your online blackjack game
2. Click "Start Scanning" in the counter window
3. Play as normal - the count updates automatically
4. Click "Reset Count" when a new shoe begins

## System Requirements

- Linux (X11 display server)
- Python 3.7+
- pip3

## Documentation

- [Installation Guide](INSTALL.md) - Detailed setup instructions
- [Usage Guide](USAGE.md) - How to use the application effectively

## How It Works

### Hi-Lo Counting System

The application implements the proven Hi-Lo card counting method:

| Card | Value |
|------|-------|
| 2-6 | +1 |
| 7-9 | 0 |
| 10-A | -1 |

**True Count** = Running Count ÷ Decks Remaining

A positive true count indicates player advantage, while negative indicates dealer advantage.

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
✅ Card counting logic (Hi-Lo system)
✅ True count calculation
✅ GUI with live updates
✅ Betting recommendations

⚠️ **Note**: Card detection accuracy depends on screen quality, card visibility, and casino interface. The current implementation uses contour detection - for production use, consider implementing template matching or machine learning models for your specific casino.

## Contributing

Contributions are welcome! Areas for improvement:
- Enhanced card detection with ML models
- Template matching for specific online casinos
- Multi-monitor support configuration
- Region selection for targeted scanning
- Additional counting systems (KO, Omega II, etc.)

## License

This project is provided for educational purposes. Users must comply with all applicable laws and regulations.

## Disclaimer

This software is provided "as is" without warranty of any kind. The authors are not responsible for any losses incurred through use of this software. Gambling involves risk - never bet more than you can afford to lose.
