#!/usr/bin/env python3
"""
Blackjack Card Scanner and Counter
Real-time card detection with full deck composition tracking
and optimal bet sizing using Kelly Criterion
"""

import cv2
import numpy as np
import mss
import time
from collections import defaultdict
import tkinter as tk
from tkinter import ttk
import threading


class CardDetector:
    """Detects playing cards from screen captures using computer vision"""

    def __init__(self):
        self.card_templates = {}
        self.card_ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

    def detect_cards(self, frame):
        """
        Detect cards in the given frame using contour detection and pattern matching
        Returns list of detected card ranks
        """
        detected_cards = []

        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        # Find contours
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # Filter contours that could be cards
        for contour in contours:
            area = cv2.contourArea(contour)

            # Cards should have a reasonable area (adjust based on screen size)
            if 1000 < area < 50000:
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)

                # Cards have an aspect ratio around 1.4 (poker card ratio)
                aspect_ratio = float(h) / w if w > 0 else 0

                if 1.2 < aspect_ratio < 1.6:
                    # Extract card region
                    card_roi = frame[y:y+h, x:x+w]

                    # Attempt to identify the card
                    card_rank = self._identify_card(card_roi)
                    if card_rank:
                        detected_cards.append(card_rank)

        return detected_cards

    def _identify_card(self, card_roi):
        """
        Identify card rank from card region of interest
        This is a simplified implementation - in production, you'd use template matching
        or a trained ML model for better accuracy
        """
        # For demonstration, we'll use OCR-like pattern matching
        # In a real implementation, you'd use pre-trained templates or neural networks

        # Extract the corner region where rank is typically displayed
        h, w = card_roi.shape[:2]
        corner = card_roi[0:int(h*0.25), 0:int(w*0.25)]

        # This is a placeholder - real implementation would do actual OCR
        # or template matching with pre-loaded card images
        return None


class CompositionTracker:
    """
    Full deck composition tracking system
    Tracks every card remaining in the shoe and calculates exact advantage
    """

    def __init__(self, num_decks=8):
        self.num_decks = num_decks
        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

        # Initialize remaining cards (4 per deck for each rank)
        self.remaining = {}
        self.reset()

        # Store original composition for reference
        self.initial_cards = dict(self.remaining)

    def reset(self):
        """Reset to full shoe"""
        self.remaining = {rank: 4 * self.num_decks for rank in self.ranks}
        self.cards_seen = []

    def add_card(self, rank):
        """Record a seen card and update composition"""
        if rank in self.remaining and self.remaining[rank] > 0:
            self.remaining[rank] -= 1
            self.cards_seen.append(rank)
            return True
        return False

    def get_total_remaining(self):
        """Get total number of cards remaining in shoe"""
        return sum(self.remaining.values())

    def get_cards_dealt(self):
        """Get total number of cards dealt"""
        return len(self.cards_seen)

    def get_composition_percentage(self, rank):
        """Get percentage of specific rank in remaining cards"""
        total = self.get_total_remaining()
        if total == 0:
            return 0.0
        return (self.remaining[rank] / total) * 100

    def calculate_player_advantage(self):
        """
        Calculate exact player advantage based on current deck composition
        Uses effect of removal (EOR) values for each rank

        Returns: advantage as percentage (e.g., 0.5 = 0.5% player advantage)
        """
        total_remaining = self.get_total_remaining()

        if total_remaining == 0:
            return 0.0

        # Effect of Removal (EOR) values - how much each card affects player advantage
        # These are approximate values based on blackjack basic strategy simulations
        # Positive EOR = removing helps player, Negative EOR = removing hurts player
        eor_values = {
            '2': 0.40,   # Removing 2s helps player
            '3': 0.43,   # Removing 3s helps player
            '4': 0.52,   # Removing 4s helps player (most beneficial)
            '5': 0.67,   # Removing 5s helps player significantly
            '6': 0.45,   # Removing 6s helps player
            '7': 0.30,   # Removing 7s slightly helps player
            '8': 0.01,   # Removing 8s nearly neutral
            '9': -0.19,  # Removing 9s slightly hurts player
            '10': -0.51, # Removing 10s hurts player
            'J': -0.51,  # Face cards hurt player when removed
            'Q': -0.51,
            'K': -0.51,
            'A': -0.59,  # Removing aces hurts player most
        }

        # Calculate expected composition for neutral shoe
        expected_per_rank = 4 * self.num_decks / 13
        expected_percentage = (expected_per_rank / (52 * self.num_decks)) * 100

        # Calculate advantage based on deviation from expected composition
        advantage = 0.0

        for rank in self.ranks:
            current_percentage = self.get_composition_percentage(rank)
            expected = (self.initial_cards[rank] / sum(self.initial_cards.values())) * 100

            # If this rank is depleted more than expected, that's equivalent to removal
            cards_removed = self.initial_cards[rank] - self.remaining[rank]
            expected_removed = self.get_cards_dealt() * (self.initial_cards[rank] / sum(self.initial_cards.values()))

            excess_removal = cards_removed - expected_removed

            # Apply EOR to calculate advantage contribution
            if excess_removal != 0:
                advantage += (excess_removal / self.get_total_remaining()) * eor_values[rank] * 100

        return advantage

    def get_kelly_bet(self, bankroll_units=100, edge_threshold=0.005):
        """
        Calculate optimal bet size using Kelly Criterion

        Args:
            bankroll_units: Total bankroll in betting units
            edge_threshold: Minimum edge required to bet (default 0.5%)

        Returns: Optimal bet size in units
        """
        advantage = self.calculate_player_advantage() / 100  # Convert to decimal

        # Don't bet if edge is negative or below threshold
        if advantage < edge_threshold:
            return 1.0  # Minimum bet

        # Kelly Criterion: f* = edge / variance
        # For blackjack, variance is approximately 1.3
        variance = 1.3
        kelly_fraction = advantage / variance

        # Use fractional Kelly (1/4 Kelly) for risk management
        fractional_kelly = 0.25
        optimal_fraction = kelly_fraction * fractional_kelly

        # Calculate bet in units
        optimal_bet = bankroll_units * optimal_fraction

        # Round to reasonable bet sizes and enforce limits
        optimal_bet = max(1.0, min(optimal_bet, bankroll_units * 0.1))  # Max 10% of bankroll
        optimal_bet = round(optimal_bet * 2) / 2  # Round to nearest 0.5 units

        return optimal_bet

    def get_penetration_percentage(self):
        """Get shoe penetration (percentage of cards dealt)"""
        total_cards = sum(self.initial_cards.values())
        dealt = self.get_cards_dealt()
        return (dealt / total_cards) * 100 if total_cards > 0 else 0

    def calculate_dealer_bust_probability(self):
        """
        Calculate dealer bust probability based on current deck composition

        Returns weighted average dealer bust probability across all possible dealer upcards
        Higher values = more likely dealer busts = better for player
        """
        total_remaining = self.get_total_remaining()

        if total_remaining == 0:
            return 0.0

        # Base dealer bust probabilities for each upcard (with S17 rules, neutral deck)
        # These are the probabilities when dealer must hit to 17
        base_bust_rates = {
            '2': 35.30,   # Dealer shows 2
            '3': 37.56,   # Dealer shows 3
            '4': 40.28,   # Dealer shows 4
            '5': 42.89,   # Dealer shows 5
            '6': 42.08,   # Dealer shows 6
            '7': 25.99,   # Dealer shows 7
            '8': 23.86,   # Dealer shows 8
            '9': 23.34,   # Dealer shows 9
            '10': 21.43,  # Dealer shows 10
            'J': 21.43,   # Dealer shows J
            'Q': 21.43,   # Dealer shows Q
            'K': 21.43,   # Dealer shows K
            'A': 11.65,   # Dealer shows A
        }

        # Calculate how composition affects bust probability
        # More high cards (10s) remaining = higher dealer bust probability
        # More low cards remaining = lower dealer bust probability

        # Get percentage of 10-value cards in remaining deck
        ten_value_cards = (self.remaining['10'] + self.remaining['J'] +
                          self.remaining['Q'] + self.remaining['K'])
        ten_percentage = (ten_value_cards / total_remaining) if total_remaining > 0 else 0

        # Normal 10-value percentage is 4/13 ≈ 30.77%
        normal_ten_percentage = 4.0 / 13.0
        ten_richness = ten_percentage / normal_ten_percentage  # >1 = rich in tens, <1 = poor in tens

        # Get percentage of low cards (2-6) in remaining deck
        low_cards = sum(self.remaining[rank] for rank in ['2', '3', '4', '5', '6'])
        low_percentage = (low_cards / total_remaining) if total_remaining > 0 else 0

        # Normal low card percentage is 5/13 ≈ 38.46%
        normal_low_percentage = 5.0 / 13.0
        low_richness = low_percentage / normal_low_percentage  # >1 = rich in lows, <1 = poor in lows

        # Adjustment factor: more 10s = higher bust rate, more low cards = lower bust rate
        # Each 10% increase in ten-richness adds ~3% to bust probability
        # Each 10% increase in low-richness subtracts ~2% from bust probability
        adjustment = ((ten_richness - 1.0) * 15.0) - ((low_richness - 1.0) * 10.0)

        # Calculate weighted average bust probability across all possible dealer upcards
        weighted_bust_prob = 0.0
        total_weight = 0.0

        for rank in self.ranks:
            if self.remaining[rank] > 0:
                # Weight by probability of this card being dealer upcard
                weight = self.remaining[rank] / total_remaining
                # Adjust base bust rate by composition
                adjusted_bust_rate = base_bust_rates[rank] + adjustment
                # Clamp between 5% and 60%
                adjusted_bust_rate = max(5.0, min(60.0, adjusted_bust_rate))

                weighted_bust_prob += adjusted_bust_rate * weight
                total_weight += weight

        if total_weight > 0:
            return weighted_bust_prob / total_weight

        return 28.0  # Default average dealer bust rate

    def get_dealer_bust_for_upcard(self, upcard):
        """
        Get dealer bust probability for a specific dealer upcard

        Args:
            upcard: Dealer's upcard rank ('2'-'9', '10', 'J', 'Q', 'K', 'A')

        Returns: Bust probability percentage for that specific upcard
        """
        total_remaining = self.get_total_remaining()

        if total_remaining == 0 or upcard not in self.ranks:
            return 0.0

        # Base bust rates
        base_bust_rates = {
            '2': 35.30, '3': 37.56, '4': 40.28, '5': 42.89, '6': 42.08,
            '7': 25.99, '8': 23.86, '9': 23.34,
            '10': 21.43, 'J': 21.43, 'Q': 21.43, 'K': 21.43, 'A': 11.65,
        }

        # Calculate composition adjustment
        ten_value_cards = (self.remaining['10'] + self.remaining['J'] +
                          self.remaining['Q'] + self.remaining['K'])
        ten_percentage = (ten_value_cards / total_remaining) if total_remaining > 0 else 0
        normal_ten_percentage = 4.0 / 13.0
        ten_richness = ten_percentage / normal_ten_percentage

        low_cards = sum(self.remaining[rank] for rank in ['2', '3', '4', '5', '6'])
        low_percentage = (low_cards / total_remaining) if total_remaining > 0 else 0
        normal_low_percentage = 5.0 / 13.0
        low_richness = low_percentage / normal_low_percentage

        adjustment = ((ten_richness - 1.0) * 15.0) - ((low_richness - 1.0) * 10.0)

        adjusted_bust_rate = base_bust_rates[upcard] + adjustment
        return max(5.0, min(60.0, adjusted_bust_rate))


class StrategyEngine:
    """
    Blackjack strategy engine with basic strategy and composition-dependent deviations
    """

    def __init__(self, composition_tracker):
        self.composition_tracker = composition_tracker

    def get_hand_value(self, cards):
        """
        Calculate hand value(s) for a list of cards
        Returns (hard_total, soft_total) or (total, None) if no ace
        """
        total = 0
        aces = 0

        for card in cards:
            if card in ['J', 'Q', 'K']:
                total += 10
            elif card == 'A':
                aces += 1
                total += 11
            else:
                total += int(card)

        # Adjust for aces
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1

        if aces > 0:
            # Soft hand
            return (total, total)
        else:
            # Hard hand
            return (total, None)

    def is_pair(self, cards):
        """Check if hand is a pair"""
        if len(cards) != 2:
            return False

        # Normalize 10-value cards
        card1 = '10' if cards[0] in ['10', 'J', 'Q', 'K'] else cards[0]
        card2 = '10' if cards[1] in ['10', 'J', 'Q', 'K'] else cards[1]

        return card1 == card2

    def get_basic_strategy_action(self, player_cards, dealer_upcard, can_double=True, can_split=True, can_surrender=True):
        """
        Get basic strategy action for given situation

        Args:
            player_cards: List of card ranks (e.g., ['10', 'K'] or ['A', '5'])
            dealer_upcard: Dealer's upcard rank
            can_double: Whether doubling is allowed
            can_split: Whether splitting is allowed
            can_surrender: Whether surrender is allowed

        Returns: Recommended action string
        """
        # Normalize dealer upcard
        dealer_value = 10 if dealer_upcard in ['J', 'Q', 'K'] else (11 if dealer_upcard == 'A' else int(dealer_upcard))

        # Check for pair first
        if can_split and self.is_pair(player_cards):
            return self._get_pair_strategy(player_cards[0], dealer_value, can_double)

        # Get hand values
        hard_total, soft_total = self.get_hand_value(player_cards)

        # Check for soft hands (has ace counted as 11)
        if soft_total is not None and hard_total != soft_total:
            return self._get_soft_strategy(hard_total, dealer_value, can_double)

        # Hard hands
        return self._get_hard_strategy(hard_total, dealer_value, can_double, can_surrender)

    def _get_pair_strategy(self, card, dealer_value, can_double):
        """Basic strategy for pairs"""
        # Normalize to rank
        rank = '10' if card in ['10', 'J', 'Q', 'K'] else card

        if rank == 'A':
            return "SPLIT"
        elif rank == '10':
            return "STAND"
        elif rank == '9':
            if dealer_value in [7, 10, 11]:
                return "STAND"
            return "SPLIT"
        elif rank == '8':
            return "SPLIT"
        elif rank == '7':
            if dealer_value <= 7:
                return "SPLIT"
            return "HIT"
        elif rank == '6':
            if dealer_value <= 6:
                return "SPLIT"
            return "HIT"
        elif rank == '5':
            if dealer_value <= 9:
                return "DOUBLE" if can_double else "HIT"
            return "HIT"
        elif rank == '4':
            if dealer_value in [5, 6]:
                return "SPLIT"
            return "HIT"
        elif rank in ['2', '3']:
            if dealer_value <= 7:
                return "SPLIT"
            return "HIT"

        return "HIT"

    def _get_soft_strategy(self, total, dealer_value, can_double):
        """Basic strategy for soft hands (hands with ace counted as 11)"""
        if total >= 19:
            return "STAND"
        elif total == 18:
            if dealer_value <= 6:
                return "DOUBLE" if can_double else "STAND"
            elif dealer_value in [7, 8]:
                return "STAND"
            else:
                return "HIT"
        elif total == 17:
            if dealer_value in [3, 4, 5, 6]:
                return "DOUBLE" if can_double else "HIT"
            return "HIT"
        elif total in [15, 16]:
            if dealer_value in [4, 5, 6]:
                return "DOUBLE" if can_double else "HIT"
            return "HIT"
        elif total in [13, 14]:
            if dealer_value in [5, 6]:
                return "DOUBLE" if can_double else "HIT"
            return "HIT"
        else:
            return "HIT"

    def _get_hard_strategy(self, total, dealer_value, can_double, can_surrender):
        """Basic strategy for hard hands"""
        if total >= 17:
            return "STAND"
        elif total == 16:
            if can_surrender and dealer_value in [9, 10, 11]:
                return "SURRENDER"
            if dealer_value <= 6:
                return "STAND"
            return "HIT"
        elif total == 15:
            if can_surrender and dealer_value == 10:
                return "SURRENDER"
            if dealer_value <= 6:
                return "STAND"
            return "HIT"
        elif total == 14:
            if dealer_value <= 6:
                return "STAND"
            return "HIT"
        elif total == 13:
            if dealer_value <= 6:
                return "STAND"
            return "HIT"
        elif total == 12:
            if dealer_value in [4, 5, 6]:
                return "STAND"
            return "HIT"
        elif total == 11:
            return "DOUBLE" if can_double else "HIT"
        elif total == 10:
            if dealer_value <= 9:
                return "DOUBLE" if can_double else "HIT"
            return "HIT"
        elif total == 9:
            if dealer_value in [3, 4, 5, 6]:
                return "DOUBLE" if can_double else "HIT"
            return "HIT"
        else:
            return "HIT"

    def get_composition_deviation(self, player_cards, dealer_upcard, basic_action):
        """
        Check if composition warrants deviation from basic strategy

        Returns: (should_deviate, new_action, reason) or (False, None, None)
        """
        advantage = self.composition_tracker.calculate_player_advantage()

        # Common composition-dependent strategy deviations
        hard_total, soft_total = self.get_hand_value(player_cards)
        dealer_value = 10 if dealer_upcard in ['J', 'Q', 'K'] else (11 if dealer_upcard == 'A' else int(dealer_upcard))

        # 16 vs 10: Stand instead of hit/surrender at high counts
        if hard_total == 16 and dealer_value == 10 and advantage >= 0.5:
            if basic_action in ["HIT", "SURRENDER"]:
                return (True, "STAND", f"High count (+{advantage:.1f}%) favors standing")

        # 15 vs 10: Stand instead of surrender at very high counts
        if hard_total == 15 and dealer_value == 10 and advantage >= 1.0:
            if basic_action == "SURRENDER":
                return (True, "STAND", f"Very high count (+{advantage:.1f}%) favors standing")

        # 12 vs 3: Stand instead of hit at high counts
        if hard_total == 12 and dealer_value == 3 and advantage >= 0.8:
            if basic_action == "HIT":
                return (True, "STAND", f"High count (+{advantage:.1f}%) favors standing")

        # 12 vs 2: Stand instead of hit at high counts
        if hard_total == 12 and dealer_value == 2 and advantage >= 1.0:
            if basic_action == "HIT":
                return (True, "STAND", f"High count (+{advantage:.1f}%) favors standing")

        # 10 vs 10: Double at very high counts
        if hard_total == 10 and dealer_value == 10 and advantage >= 1.5:
            if basic_action == "HIT":
                return (True, "DOUBLE", f"Very high count (+{advantage:.1f}%) favors doubling")

        # 10 vs A: Double at very high counts
        if hard_total == 10 and dealer_value == 11 and advantage >= 1.5:
            if basic_action == "HIT":
                return (True, "DOUBLE", f"Very high count (+{advantage:.1f}%) favors doubling")

        # 9 vs 2: Double at high counts
        if hard_total == 9 and dealer_value == 2 and advantage >= 0.5:
            if basic_action == "HIT":
                return (True, "DOUBLE", f"High count (+{advantage:.1f}%) favors doubling")

        # No deviation
        return (False, None, None)

    def get_recommended_action(self, player_cards, dealer_upcard, can_double=True, can_split=True, can_surrender=True):
        """
        Get complete recommendation including composition deviations

        Returns: (action, is_deviation, reason)
        """
        # Get basic strategy action
        basic_action = self.get_basic_strategy_action(
            player_cards, dealer_upcard, can_double, can_split, can_surrender
        )

        # Check for composition-dependent deviation
        should_deviate, deviation_action, reason = self.get_composition_deviation(
            player_cards, dealer_upcard, basic_action
        )

        if should_deviate:
            return (deviation_action, True, reason)
        else:
            return (basic_action, False, "Basic strategy")


class ScreenCapture:
    """Handles screen capture for card detection"""

    def __init__(self, monitor_number=1):
        self.sct = mss.mss()
        self.monitor_number = monitor_number
        self.monitor = self.sct.monitors[monitor_number]

    def capture_frame(self):
        """Capture a single frame from the screen"""
        screenshot = self.sct.grab(self.monitor)

        # Convert to numpy array
        frame = np.array(screenshot)

        # Convert from BGRA to BGR
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        return frame

    def set_region(self, x, y, width, height):
        """Set a specific region to capture"""
        self.monitor = {
            "top": y,
            "left": x,
            "width": width,
            "height": height
        }


class BlackjackCounterGUI:
    """GUI for displaying composition tracking and optimal betting"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Blackjack Composition Tracker")
        self.root.geometry("600x850")
        self.root.attributes('-topmost', True)  # Keep on top

        # Create display elements
        self.create_widgets()

        # Initialize components
        self.screen_capture = ScreenCapture()
        self.card_detector = CardDetector()
        self.composition_tracker = CompositionTracker(num_decks=8)
        self.strategy_engine = StrategyEngine(self.composition_tracker)

        # Control flags
        self.is_running = False
        self.scan_thread = None

    def create_widgets(self):
        """Create GUI widgets"""
        # Title
        title_label = tk.Label(
            self.root,
            text="Blackjack Composition Tracker",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)

        # Optimal Bet Display (PRIMARY)
        bet_frame = tk.Frame(self.root, bg="#f0f0f0", relief=tk.RAISED, bd=2)
        bet_frame.pack(pady=15, padx=20, fill=tk.X)

        tk.Label(
            bet_frame,
            text="Optimal Bet:",
            font=("Arial", 14, "bold"),
            bg="#f0f0f0"
        ).pack(pady=5)

        self.bet_label = tk.Label(
            bet_frame,
            text="1.0 units",
            font=("Arial", 32, "bold"),
            fg="blue",
            bg="#f0f0f0"
        )
        self.bet_label.pack(pady=5)

        # Player Advantage Display
        advantage_frame = tk.Frame(self.root)
        advantage_frame.pack(pady=10)

        tk.Label(
            advantage_frame,
            text="Player Advantage:",
            font=("Arial", 12)
        ).pack(side=tk.LEFT)

        self.advantage_label = tk.Label(
            advantage_frame,
            text="0.00%",
            font=("Arial", 16, "bold"),
            fg="gray"
        )
        self.advantage_label.pack(side=tk.LEFT, padx=10)

        # Dealer Bust Probability Display
        bust_frame = tk.Frame(self.root)
        bust_frame.pack(pady=10)

        tk.Label(
            bust_frame,
            text="Dealer Bust Chance:",
            font=("Arial", 12)
        ).pack(side=tk.LEFT)

        self.bust_label = tk.Label(
            bust_frame,
            text="28.0%",
            font=("Arial", 16, "bold"),
            fg="gray"
        )
        self.bust_label.pack(side=tk.LEFT, padx=10)

        # Cards Remaining Display
        cards_frame = tk.Frame(self.root)
        cards_frame.pack(pady=5)

        tk.Label(
            cards_frame,
            text="Cards Remaining:",
            font=("Arial", 11)
        ).pack(side=tk.LEFT)

        self.cards_remaining_label = tk.Label(
            cards_frame,
            text="416",
            font=("Arial", 12)
        )
        self.cards_remaining_label.pack(side=tk.LEFT, padx=10)

        # Penetration Display
        penetration_frame = tk.Frame(self.root)
        penetration_frame.pack(pady=5)

        tk.Label(
            penetration_frame,
            text="Shoe Penetration:",
            font=("Arial", 11)
        ).pack(side=tk.LEFT)

        self.penetration_label = tk.Label(
            penetration_frame,
            text="0.0%",
            font=("Arial", 12)
        )
        self.penetration_label.pack(side=tk.LEFT, padx=10)

        # Composition Summary (show key cards)
        comp_frame = tk.LabelFrame(self.root, text="Key Card Counts", font=("Arial", 10, "bold"))
        comp_frame.pack(pady=10, padx=20, fill=tk.X)

        self.composition_labels = {}
        # Note: 10 represents all 10-value cards (10, J, Q, K)
        key_ranks = ['5', '6', '10-val', 'A']  # Most impactful cards

        comp_grid = tk.Frame(comp_frame)
        comp_grid.pack(pady=5)

        for i, rank in enumerate(key_ranks):
            frame = tk.Frame(comp_grid)
            frame.grid(row=0, column=i, padx=10)

            display_name = rank if rank != '10-val' else '10/J/Q/K'
            tk.Label(frame, text=f"{display_name}:", font=("Arial", 10, "bold")).pack()
            initial_val = "128" if rank == '10-val' else "32"
            label = tk.Label(frame, text=initial_val, font=("Arial", 11))
            label.pack()
            self.composition_labels[rank] = label

        # Manual Card Entry Section
        card_entry_frame = tk.LabelFrame(self.root, text="Card Tracker (for Infinite Blackjack)", font=("Arial", 11, "bold"))
        card_entry_frame.pack(pady=10, padx=20, fill=tk.X)

        # Instructions
        tk.Label(
            card_entry_frame,
            text="Click cards as you see them dealt (any player, dealer, etc.)",
            font=("Arial", 9, "italic"),
            fg="gray"
        ).pack(pady=3)

        # Quick add buttons for all ranks
        button_frame = tk.Frame(card_entry_frame)
        button_frame.pack(pady=8)

        self.card_buttons = {}
        all_ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

        for i, rank in enumerate(all_ranks):
            btn = tk.Button(
                button_frame,
                text=rank,
                command=lambda r=rank: self.add_card_manual(r),
                font=("Arial", 10, "bold"),
                width=4,
                height=1
            )
            btn.grid(row=0, column=i, padx=2, pady=2)
            self.card_buttons[rank] = btn

        # Text entry for multiple cards
        multi_entry_frame = tk.Frame(card_entry_frame)
        multi_entry_frame.pack(pady=5)

        tk.Label(multi_entry_frame, text="Or enter multiple:", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        self.multi_card_entry = tk.Entry(multi_entry_frame, width=20, font=("Arial", 10))
        self.multi_card_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(
            multi_entry_frame,
            text="Add Cards",
            command=self.add_multiple_cards,
            font=("Arial", 9),
            bg="#2196F3",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)

        tk.Label(
            card_entry_frame,
            text="Format: 10,K,5,A or 10 K 5 A",
            font=("Arial", 8, "italic"),
            fg="gray"
        ).pack(pady=2)

        # Strategy Advisor Section
        strategy_frame = tk.LabelFrame(self.root, text="Strategy Advisor", font=("Arial", 11, "bold"))
        strategy_frame.pack(pady=15, padx=20, fill=tk.X)

        # Input row
        input_frame = tk.Frame(strategy_frame)
        input_frame.pack(pady=8)

        tk.Label(input_frame, text="Your Hand:", font=("Arial", 10)).grid(row=0, column=0, padx=5)
        self.player_hand_entry = tk.Entry(input_frame, width=10, font=("Arial", 11))
        self.player_hand_entry.grid(row=0, column=1, padx=5)
        self.player_hand_entry.insert(0, "10,6")

        tk.Label(input_frame, text="Dealer:", font=("Arial", 10)).grid(row=0, column=2, padx=5)
        self.dealer_upcard_entry = tk.Entry(input_frame, width=5, font=("Arial", 11))
        self.dealer_upcard_entry.grid(row=0, column=3, padx=5)
        self.dealer_upcard_entry.insert(0, "10")

        self.calc_action_button = tk.Button(
            input_frame,
            text="Get Action",
            command=self.calculate_action,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        )
        self.calc_action_button.grid(row=0, column=4, padx=10)

        # Action display
        action_display_frame = tk.Frame(strategy_frame, bg="#f0f0f0", relief=tk.RAISED, bd=2)
        action_display_frame.pack(pady=10, padx=10, fill=tk.X)

        tk.Label(
            action_display_frame,
            text="Recommended Action:",
            font=("Arial", 11, "bold"),
            bg="#f0f0f0"
        ).pack(pady=3)

        self.action_label = tk.Label(
            action_display_frame,
            text="STAND",
            font=("Arial", 28, "bold"),
            fg="#2196F3",
            bg="#f0f0f0"
        )
        self.action_label.pack(pady=5)

        self.action_reason_label = tk.Label(
            action_display_frame,
            text="Basic strategy",
            font=("Arial", 9, "italic"),
            fg="gray",
            bg="#f0f0f0"
        )
        self.action_reason_label.pack(pady=3)

        # Status message
        self.status_label = tk.Label(
            self.root,
            text="Waiting to start...",
            font=("Arial", 10, "italic"),
            fg="gray"
        )
        self.status_label.pack(pady=10)

        # Control Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        self.start_button = tk.Button(
            button_frame,
            text="Start Scanning",
            command=self.start_scanning,
            bg="green",
            fg="white",
            font=("Arial", 11, "bold"),
            width=12
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(
            button_frame,
            text="Stop Scanning",
            command=self.stop_scanning,
            bg="red",
            fg="white",
            font=("Arial", 11, "bold"),
            width=12,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = tk.Button(
            button_frame,
            text="New Shoe",
            command=self.reset_count,
            font=("Arial", 11, "bold"),
            width=12
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)

    def update_display(self):
        """Update the display with current composition and betting info"""
        advantage = self.composition_tracker.calculate_player_advantage()
        optimal_bet = self.composition_tracker.get_kelly_bet()
        cards_remaining = self.composition_tracker.get_total_remaining()
        penetration = self.composition_tracker.get_penetration_percentage()

        # Update optimal bet (main display)
        self.bet_label.config(text=f"{optimal_bet:.1f} units")

        # Color code based on bet size
        if optimal_bet >= 5.0:
            self.bet_label.config(fg="darkgreen")
            bet_color = "#d4edda"
        elif optimal_bet >= 3.0:
            self.bet_label.config(fg="green")
            bet_color = "#e8f5e9"
        elif optimal_bet >= 2.0:
            self.bet_label.config(fg="orange")
            bet_color = "#fff9e6"
        else:
            self.bet_label.config(fg="red")
            bet_color = "#ffebee"

        bet_frame = self.bet_label.master
        bet_frame.config(bg=bet_color)
        for widget in bet_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(bg=bet_color)

        # Update advantage display
        self.advantage_label.config(text=f"{advantage:+.3f}%")

        if advantage >= 1.0:
            self.advantage_label.config(fg="darkgreen")
        elif advantage >= 0.5:
            self.advantage_label.config(fg="green")
        elif advantage >= 0.0:
            self.advantage_label.config(fg="orange")
        else:
            self.advantage_label.config(fg="red")

        # Update dealer bust probability
        dealer_bust = self.composition_tracker.calculate_dealer_bust_probability()
        self.bust_label.config(text=f"{dealer_bust:.1f}%")

        # Color code: higher bust probability = better for player
        if dealer_bust >= 32.0:
            self.bust_label.config(fg="darkgreen")  # High bust chance - very good
        elif dealer_bust >= 29.0:
            self.bust_label.config(fg="green")  # Above average - good
        elif dealer_bust >= 26.0:
            self.bust_label.config(fg="orange")  # Slightly below average
        else:
            self.bust_label.config(fg="red")  # Low bust chance - bad for player

        # Update card counts
        self.cards_remaining_label.config(text=str(cards_remaining))
        self.penetration_label.config(text=f"{penetration:.1f}%")

        # Update key card composition
        for rank, label in self.composition_labels.items():
            if rank == '10-val':
                # Combine all 10-value cards (10, J, Q, K)
                count = (self.composition_tracker.remaining['10'] +
                        self.composition_tracker.remaining['J'] +
                        self.composition_tracker.remaining['Q'] +
                        self.composition_tracker.remaining['K'])
            else:
                count = self.composition_tracker.remaining[rank]
            label.config(text=str(count))

        # Update status
        if advantage >= 0.5:
            status = "FAVORABLE - Player has edge!"
        elif advantage >= 0.0:
            status = "MARGINAL - Small edge"
        else:
            status = "UNFAVORABLE - House has edge"

        self.status_label.config(
            text=status,
            fg="green" if advantage >= 0.5 else "orange" if advantage >= 0.0 else "red"
        )

    def calculate_action(self):
        """Calculate and display recommended action based on player hand and dealer upcard"""
        try:
            # Parse player hand
            player_hand_str = self.player_hand_entry.get().strip()
            player_cards = [card.strip().upper() for card in player_hand_str.split(',')]

            # Parse dealer upcard
            dealer_upcard = self.dealer_upcard_entry.get().strip().upper()

            # Validate inputs
            valid_ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
            for card in player_cards:
                if card not in valid_ranks:
                    self.action_label.config(text="INVALID HAND", fg="red")
                    self.action_reason_label.config(text="Use format: 10,6 or A,5")
                    return

            if dealer_upcard not in valid_ranks:
                self.action_label.config(text="INVALID DEALER", fg="red")
                self.action_reason_label.config(text="Enter dealer upcard (2-A)")
                return

            # Get recommended action
            action, is_deviation, reason = self.strategy_engine.get_recommended_action(
                player_cards, dealer_upcard
            )

            # Update display
            self.action_label.config(text=action)
            self.action_reason_label.config(text=reason)

            # Color code the action
            action_colors = {
                "HIT": "#FF9800",      # Orange
                "STAND": "#2196F3",    # Blue
                "DOUBLE": "#4CAF50",   # Green
                "SPLIT": "#9C27B0",    # Purple
                "SURRENDER": "#F44336" # Red
            }

            action_color = action_colors.get(action, "#2196F3")
            self.action_label.config(fg=action_color)

            # Highlight if deviation from basic strategy
            if is_deviation:
                self.action_label.config(fg="#FF5722")  # Deep orange for deviations
                self.action_reason_label.config(fg="#FF5722", font=("Arial", 9, "italic", "bold"))
            else:
                self.action_reason_label.config(fg="gray", font=("Arial", 9, "italic"))

        except Exception as e:
            self.action_label.config(text="ERROR", fg="red")
            self.action_reason_label.config(text=str(e))

    def add_card_manual(self, rank):
        """Add a single card to the composition tracker"""
        success = self.composition_tracker.add_card(rank)
        if success:
            # Visual feedback - briefly highlight the button
            self.card_buttons[rank].config(bg="#4CAF50")
            self.root.after(200, lambda: self.card_buttons[rank].config(bg="SystemButtonFace"))
            # Update the display
            self.update_display()
        else:
            # Card not available (shouldn't happen in normal use)
            self.card_buttons[rank].config(bg="#F44336")
            self.root.after(200, lambda: self.card_buttons[rank].config(bg="SystemButtonFace"))

    def add_multiple_cards(self):
        """Add multiple cards from text entry"""
        cards_str = self.multi_card_entry.get().strip().upper()
        if not cards_str:
            return

        # Parse cards - support both comma and space separation
        cards_str = cards_str.replace(',', ' ')
        cards = [c.strip() for c in cards_str.split() if c.strip()]

        valid_ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        added_count = 0

        for card in cards:
            if card in valid_ranks:
                if self.composition_tracker.add_card(card):
                    added_count += 1

        if added_count > 0:
            self.update_display()
            self.multi_card_entry.delete(0, tk.END)
            # Show feedback
            self.multi_card_entry.config(bg="#4CAF50")
            self.root.after(500, lambda: self.multi_card_entry.config(bg="white"))

    def scan_loop(self):
        """Main scanning loop running in separate thread"""
        prev_cards = set()

        while self.is_running:
            try:
                # Capture frame
                frame = self.screen_capture.capture_frame()

                # Detect cards
                detected_cards = self.card_detector.detect_cards(frame)

                # Add new cards to tracker
                current_cards = set(detected_cards)
                new_cards = current_cards - prev_cards

                for card_rank in new_cards:
                    self.composition_tracker.add_card(card_rank)

                prev_cards = current_cards

                # Update display
                self.root.after(0, self.update_display)

                # Sleep briefly to control CPU usage
                time.sleep(0.5)

            except Exception as e:
                print(f"Error in scan loop: {e}")
                time.sleep(1)

    def start_scanning(self):
        """Start the card scanning process"""
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Scanning...", fg="blue")

        # Start scanning in separate thread
        self.scan_thread = threading.Thread(target=self.scan_loop, daemon=True)
        self.scan_thread.start()

    def stop_scanning(self):
        """Stop the card scanning process"""
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Stopped", fg="gray")

    def reset_count(self):
        """Reset for new shoe"""
        self.composition_tracker.reset()
        self.update_display()
        self.status_label.config(text="New shoe - Ready to scan", fg="blue")

    def run(self):
        """Start the GUI main loop"""
        self.update_display()  # Initialize display
        self.root.mainloop()


def main():
    """Main entry point"""
    print("Blackjack Composition Tracker")
    print("=============================")
    print("Full deck composition tracking with optimal bet sizing")
    print("Starting application...")

    # Create and run the GUI
    app = BlackjackCounterGUI()
    app.run()


if __name__ == "__main__":
    main()
