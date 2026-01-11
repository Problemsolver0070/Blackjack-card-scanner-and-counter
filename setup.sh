#!/bin/bash
# Setup script for Blackjack Card Scanner and Counter

echo "Setting up Blackjack Card Scanner and Counter..."
echo "================================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

echo "Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed. Please install pip3."
    exit 1
fi

echo "pip3 found: $(pip3 --version)"

# Install required packages
echo ""
echo "Installing required Python packages..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "Setup completed successfully!"
    echo ""
    echo "To run the application:"
    echo "  python3 blackjack_counter.py"
    echo ""
    echo "Or make it executable:"
    echo "  chmod +x blackjack_counter.py"
    echo "  ./blackjack_counter.py"
else
    echo ""
    echo "Error: Failed to install dependencies."
    exit 1
fi
