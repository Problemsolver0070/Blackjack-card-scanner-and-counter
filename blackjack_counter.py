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

    def __init__(self, num_decks=6):
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
        self.root.geometry("500x450")
        self.root.attributes('-topmost', True)  # Keep on top

        # Create display elements
        self.create_widgets()

        # Initialize components
        self.screen_capture = ScreenCapture()
        self.card_detector = CardDetector()
        self.composition_tracker = CompositionTracker(num_decks=6)

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
            text="312",
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
        key_ranks = ['5', '6', '10', 'A']  # Most impactful cards

        comp_grid = tk.Frame(comp_frame)
        comp_grid.pack(pady=5)

        for i, rank in enumerate(key_ranks):
            frame = tk.Frame(comp_grid)
            frame.grid(row=0, column=i, padx=10)

            tk.Label(frame, text=f"{rank}:", font=("Arial", 10, "bold")).pack()
            label = tk.Label(frame, text="24", font=("Arial", 11))
            label.pack()
            self.composition_labels[rank] = label

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

        # Update card counts
        self.cards_remaining_label.config(text=str(cards_remaining))
        self.penetration_label.config(text=f"{penetration:.1f}%")

        # Update key card composition
        for rank, label in self.composition_labels.items():
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
