# Usage Guide

## How It Works

The Blackjack Card Scanner and Counter uses computer vision to detect cards displayed on your screen and implements **full deck composition tracking** to calculate exact player advantage and optimal bet sizing.

## Composition Tracking System

This application uses **full deck composition tracking**, which is more accurate than traditional counting systems like Hi-Lo:

### What It Tracks:
- **Every single card**: Maintains count of all 52×6 = 312 cards in a 6-deck shoe
- **13 separate ranks**: Tracks 2, 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K, A independently
- **Exact composition**: Knows precisely how many of each rank remain

### Key Metrics:

1. **Optimal Bet (PRIMARY)**: The bet size you should make in units
   - Calculated using Kelly Criterion
   - Based on your exact advantage at this moment
   - Accounts for bankroll size and variance
   - Uses 1/4 Kelly for conservative risk management

2. **Player Advantage**: Your exact edge over the house
   - Calculated using Effect of Removal (EOR) values
   - Positive = you have an edge
   - Negative = house has an edge
   - Examples: +1.5% is excellent, -0.5% is unfavorable

3. **Cards Remaining**: Total cards left in the shoe
   - Starts at 312 (for 6-deck shoe)
   - Decreases as cards are dealt

4. **Shoe Penetration**: Percentage of cards dealt
   - Important for determining when advantage is most reliable
   - Higher penetration = more accurate advantage calculation

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

The application shows several key pieces of information:

#### Primary Display:
- **Optimal Bet**: The main indicator - tells you EXACTLY how many units to bet
  - **Dark Green (≥5 units)**: Excellent opportunity
  - **Green (3-5 units)**: Very favorable
  - **Orange (2-3 units)**: Moderately favorable
  - **Red (1 unit)**: Minimum bet only

#### Secondary Metrics:
- **Player Advantage**: Your exact edge as a percentage
  - +1.0% or higher: Excellent
  - +0.5% to +1.0%: Good
  - 0% to +0.5%: Marginal
  - Negative: Unfavorable

- **Cards Remaining**: Total cards left in shoe
- **Shoe Penetration**: Percentage of shoe dealt
- **Key Card Counts**: Shows remaining 5s, 6s, 10s, and Aces (most impactful cards)

### Step 5: Reset Between Shoes

When the dealer shuffles a new shoe, click **"New Shoe"** to reset the tracker.

## Betting Strategy Using Optimal Bet Size

The application automatically calculates your optimal bet based on Kelly Criterion. Simply bet what it tells you:

| Optimal Bet | Player Advantage | Situation |
|-------------|------------------|-----------|
| 5+ units | +1.5% or higher | Excellent - Max bet |
| 3-5 units | +1.0% to +1.5% | Very favorable |
| 2-3 units | +0.7% to +1.0% | Favorable |
| 1-2 units | +0.5% to +0.7% | Slight edge |
| 1 unit | Below +0.5% | Minimum bet only |

### Understanding Units

A "unit" is your base betting amount. For example:
- If your unit is $25, and the app shows "3.0 units", bet $75
- If your unit is $10, and the app shows "5.5 units", bet $55
- If your unit is $100, and the app shows "1.0 units", bet $100

The default calculation assumes a 100-unit bankroll. Adjust your unit size accordingly:
- **Conservative**: 1 unit = 1% of bankroll
- **Moderate**: 1 unit = 1.5% of bankroll
- **Aggressive**: 1 unit = 2% of bankroll

## Tips for Best Results

1. **Clear Visibility**: Ensure cards are clearly visible on screen
2. **Consistent Lighting**: Avoid glare or dark screens
3. **Manual Verification**: Double-check the count occasionally
4. **Reset Properly**: Always reset when a new shoe begins
5. **Practice**: Test with free games before using real money

## Current Implementation

The current implementation includes:

- ✅ Screen capture functionality
- ✅ Full deck composition tracking (all 13 ranks)
- ✅ Exact player advantage calculation (EOR-based)
- ✅ Kelly Criterion optimal bet sizing
- ✅ Real-time display with bet in units
- ✅ Key card composition display
- ✅ Shoe penetration tracking

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
