# Usage Guide

## How It Works

The Blackjack Card Scanner and Counter uses computer vision to detect cards displayed on your screen and implements the Hi-Lo card counting system to give you real-time advantage information.

## Card Counting System

This application uses the **Hi-Lo counting system**, one of the most popular and effective card counting methods:

### Card Values:
- **Low cards (2-6)**: +1
- **Neutral cards (7-9)**: 0
- **High cards (10, J, Q, K, A)**: -1

### Key Metrics:

1. **Running Count**: The raw total of all cards seen
   - Add +1 for each low card (2-6)
   - Add -1 for each high card (10-A)
   - Add 0 for neutral cards (7-9)

2. **True Count**: Running Count ÷ Decks Remaining
   - This adjusts for how many cards are left
   - More accurate indicator of advantage

3. **Decks Remaining**: Estimated based on cards seen
   - Starts at 6.0 decks (standard shoe)
   - Decreases as more cards are detected

## Using the Application

### Step 1: Launch the Application

```bash
python3 blackjack_counter.py
```

A window will appear with the card counting interface.

### Step 2: Position Your Blackjack Game

- Open your online blackjack game in a browser or application
- Make sure the cards are clearly visible on screen
- The application scans the entire primary monitor by default

### Step 3: Start Scanning

Click the **"Start Scanning"** button to begin monitoring your screen.

### Step 4: Interpret the Display

The application shows:

- **True Count**: Main indicator
  - **Green (≥ +2)**: Favorable - Increase your bet
  - **Red (≤ -2)**: Unfavorable - Bet minimum
  - **Blue (-2 to +2)**: Neutral - Standard bet

- **Running Count**: Raw count total
- **Decks Remaining**: Estimated decks left
- **Recommendation**: Betting advice

### Step 5: Reset Between Shoes

When the dealer shuffles a new shoe, click **"Reset Count"** to start fresh.

## Betting Strategy Based on True Count

| True Count | Recommendation | Betting Unit |
|-----------|----------------|--------------|
| ≥ +3 | Highly Favorable | 8x minimum |
| +2 | Favorable | 4x minimum |
| +1 | Slight Advantage | 2x minimum |
| 0 | Neutral | 1x minimum |
| -1 | Slight Disadvantage | 1x minimum |
| ≤ -2 | Unfavorable | Minimum bet |

## Tips for Best Results

1. **Clear Visibility**: Ensure cards are clearly visible on screen
2. **Consistent Lighting**: Avoid glare or dark screens
3. **Manual Verification**: Double-check the count occasionally
4. **Reset Properly**: Always reset when a new shoe begins
5. **Practice**: Test with free games before using real money

## Current Limitations

The current implementation includes:

- ✅ Screen capture functionality
- ✅ Card counting logic (Hi-Lo system)
- ✅ True count calculation
- ✅ Real-time display with recommendations
- ✅ GUI controls

**Note**: The card detection uses contour-based detection. For optimal accuracy:
- Cards should be clearly visible with good contrast
- Consider training custom templates for specific online casinos
- Manual card entry may be more reliable for some setups

## Advanced: Improving Card Detection

To improve card detection accuracy for your specific online casino:

1. Capture screenshots of cards from your casino
2. Create template images for each card rank
3. Update the `CardDetector._identify_card()` method with template matching
4. Use OpenCV's `cv2.matchTemplate()` for better recognition

## Legal and Ethical Considerations

**Important**:
- Card counting is a legal strategy in most jurisdictions
- However, casinos may ban players who count cards
- Online casinos may use continuous shuffle machines (CSMs) which make counting ineffective
- Use this tool responsibly and be aware of your casino's terms of service
- This is for educational purposes

## Troubleshooting

### Cards Not Being Detected

- Check that the scan is running (button shows "Stop Scanning")
- Verify cards are clearly visible on screen
- Ensure good contrast between cards and background
- Try adjusting the threshold values in `CardDetector.detect_cards()`

### Incorrect Count

- Reset the count and start over
- Verify all cards are being detected
- Check for double-counting (same card detected multiple times)

### Performance Issues

- Reduce scan frequency by increasing `time.sleep()` value
- Close other applications to free up CPU
- Use a specific screen region instead of full screen

## Support

For issues, improvements, or questions, please open an issue on the GitHub repository.
