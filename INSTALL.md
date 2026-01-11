# Installation Guide

## System Requirements

- Linux operating system
- Python 3.7 or higher
- X11 display server (for screen capture)
- pip3 (Python package manager)

## Quick Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Blackjack-card-scanner-and-counter
```

2. Run the setup script:
```bash
chmod +x setup.sh
./setup.sh
```

3. Run the application:
```bash
python3 blackjack_counter.py
```

## Manual Installation

If you prefer to install manually:

1. Install Python dependencies:
```bash
pip3 install -r requirements.txt
```

2. Make the script executable (optional):
```bash
chmod +x blackjack_counter.py
```

3. Run the application:
```bash
./blackjack_counter.py
```

## Dependencies

The following Python packages will be installed:

- **opencv-python**: For computer vision and card detection
- **numpy**: For numerical operations
- **mss**: For efficient screen capture
- **pillow**: For image processing

## Troubleshooting

### Screen Capture Issues

If screen capture doesn't work:
- Ensure you're running on X11 (not Wayland)
- Check display permissions
- Try running with: `DISPLAY=:0 python3 blackjack_counter.py`

### Permission Errors

If you get permission errors during installation:
```bash
pip3 install --user -r requirements.txt
```

### Missing System Libraries

On Ubuntu/Debian, you may need:
```bash
sudo apt-get update
sudo apt-get install python3-tk python3-dev
sudo apt-get install libgl1-mesa-glx libglib2.0-0
```

On Fedora/RHEL:
```bash
sudo dnf install python3-tkinter
sudo dnf install mesa-libGL
```

## Verifying Installation

To verify everything is installed correctly:
```bash
python3 -c "import cv2, mss, numpy, PIL; print('All dependencies installed successfully!')"
```

## Running the Application

Once installed, simply run:
```bash
python3 blackjack_counter.py
```

The GUI will appear with controls to:
- **Start Scanning**: Begin monitoring your screen for cards
- **Stop Scanning**: Pause the monitoring
- **Reset Count**: Reset the counter when a new shoe starts

## Usage Notes

1. Position the blackjack game window where it's visible on your screen
2. Start the application
3. Click "Start Scanning" to begin monitoring
4. The application will display:
   - True Count (the adjusted count based on remaining decks)
   - Running Count (raw count)
   - Decks Remaining (estimated)
   - Betting Recommendation

## Performance

- The application scans approximately every 0.5 seconds
- Minimal CPU usage when idle
- Supports multi-monitor setups
