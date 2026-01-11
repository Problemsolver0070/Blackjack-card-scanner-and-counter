#!/usr/bin/env python3
"""
Blackjack Card Scanner and Counter
Real-time card detection and counting from screen capture
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
        self.card_values = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
            '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11
        }

    def detect_cards(self, frame):
        """
        Detect cards in the given frame using contour detection and pattern matching
        Returns list of detected card values
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
                    card_value = self._identify_card(card_roi)
                    if card_value:
                        detected_cards.append(card_value)

        return detected_cards

    def _identify_card(self, card_roi):
        """
        Identify card value from card region of interest
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


class CardCounter:
    """Implements Hi-Lo card counting system"""

    def __init__(self):
        self.running_count = 0
        self.decks_remaining = 6.0  # Standard 6-deck shoe
        self.cards_seen = []

        # Hi-Lo counting values
        self.count_values = {
            '2': 1, '3': 1, '4': 1, '5': 1, '6': 1,  # Low cards: +1
            '7': 0, '8': 0, '9': 0,                   # Neutral: 0
            '10': -1, 'J': -1, 'Q': -1, 'K': -1, 'A': -1  # High cards: -1
        }

    def add_card(self, card_value):
        """Add a seen card and update the count"""
        if card_value in self.count_values:
            self.running_count += self.count_values[card_value]
            self.cards_seen.append(card_value)

            # Update decks remaining
            cards_per_deck = 52
            total_cards = 6 * cards_per_deck
            self.decks_remaining = (total_cards - len(self.cards_seen)) / cards_per_deck

            if self.decks_remaining < 0.5:
                self.decks_remaining = 0.5  # Minimum estimate

    def get_true_count(self):
        """Calculate and return the true count"""
        if self.decks_remaining > 0:
            return self.running_count / self.decks_remaining
        return 0

    def reset(self):
        """Reset the counter for a new shoe"""
        self.running_count = 0
        self.decks_remaining = 6.0
        self.cards_seen = []

    def get_recommendation(self):
        """Get betting recommendation based on true count"""
        true_count = self.get_true_count()

        if true_count >= 2:
            return "FAVORABLE - Increase bet"
        elif true_count <= -2:
            return "UNFAVORABLE - Minimum bet"
        else:
            return "NEUTRAL - Standard bet"


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
    """GUI for displaying card counting information"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Blackjack Card Counter")
        self.root.geometry("400x300")
        self.root.attributes('-topmost', True)  # Keep on top

        # Create display elements
        self.create_widgets()

        # Initialize components
        self.screen_capture = ScreenCapture()
        self.card_detector = CardDetector()
        self.card_counter = CardCounter()

        # Control flags
        self.is_running = False
        self.scan_thread = None

    def create_widgets(self):
        """Create GUI widgets"""
        # Title
        title_label = tk.Label(
            self.root,
            text="Blackjack Card Counter",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)

        # True Count Display
        count_frame = tk.Frame(self.root)
        count_frame.pack(pady=20)

        tk.Label(
            count_frame,
            text="True Count:",
            font=("Arial", 14)
        ).pack(side=tk.LEFT)

        self.true_count_label = tk.Label(
            count_frame,
            text="0.0",
            font=("Arial", 24, "bold"),
            fg="blue"
        )
        self.true_count_label.pack(side=tk.LEFT, padx=10)

        # Running Count Display
        running_frame = tk.Frame(self.root)
        running_frame.pack(pady=10)

        tk.Label(
            running_frame,
            text="Running Count:",
            font=("Arial", 12)
        ).pack(side=tk.LEFT)

        self.running_count_label = tk.Label(
            running_frame,
            text="0",
            font=("Arial", 14)
        )
        self.running_count_label.pack(side=tk.LEFT, padx=10)

        # Decks Remaining Display
        decks_frame = tk.Frame(self.root)
        decks_frame.pack(pady=10)

        tk.Label(
            decks_frame,
            text="Decks Remaining:",
            font=("Arial", 12)
        ).pack(side=tk.LEFT)

        self.decks_label = tk.Label(
            decks_frame,
            text="6.0",
            font=("Arial", 14)
        )
        self.decks_label.pack(side=tk.LEFT, padx=10)

        # Recommendation Display
        self.recommendation_label = tk.Label(
            self.root,
            text="NEUTRAL - Standard bet",
            font=("Arial", 12, "italic"),
            fg="gray"
        )
        self.recommendation_label.pack(pady=20)

        # Control Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        self.start_button = tk.Button(
            button_frame,
            text="Start Scanning",
            command=self.start_scanning,
            bg="green",
            fg="white",
            font=("Arial", 12)
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(
            button_frame,
            text="Stop Scanning",
            command=self.stop_scanning,
            bg="red",
            fg="white",
            font=("Arial", 12),
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = tk.Button(
            button_frame,
            text="Reset Count",
            command=self.reset_count,
            font=("Arial", 12)
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)

    def update_display(self):
        """Update the display with current count information"""
        true_count = self.card_counter.get_true_count()
        running_count = self.card_counter.running_count
        decks_remaining = self.card_counter.decks_remaining
        recommendation = self.card_counter.get_recommendation()

        # Update labels
        self.true_count_label.config(text=f"{true_count:.1f}")
        self.running_count_label.config(text=str(running_count))
        self.decks_label.config(text=f"{decks_remaining:.1f}")
        self.recommendation_label.config(text=recommendation)

        # Color code the true count
        if true_count >= 2:
            self.true_count_label.config(fg="green")
            self.recommendation_label.config(fg="green")
        elif true_count <= -2:
            self.true_count_label.config(fg="red")
            self.recommendation_label.config(fg="red")
        else:
            self.true_count_label.config(fg="blue")
            self.recommendation_label.config(fg="gray")

    def scan_loop(self):
        """Main scanning loop running in separate thread"""
        prev_cards = set()

        while self.is_running:
            try:
                # Capture frame
                frame = self.screen_capture.capture_frame()

                # Detect cards
                detected_cards = self.card_detector.detect_cards(frame)

                # Add new cards to counter
                current_cards = set(detected_cards)
                new_cards = current_cards - prev_cards

                for card in new_cards:
                    self.card_counter.add_card(card)

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

        # Start scanning in separate thread
        self.scan_thread = threading.Thread(target=self.scan_loop, daemon=True)
        self.scan_thread.start()

    def stop_scanning(self):
        """Stop the card scanning process"""
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def reset_count(self):
        """Reset the card counter"""
        self.card_counter.reset()
        self.update_display()

    def run(self):
        """Start the GUI main loop"""
        self.root.mainloop()


def main():
    """Main entry point"""
    print("Blackjack Card Scanner and Counter")
    print("===================================")
    print("Starting application...")

    # Create and run the GUI
    app = BlackjackCounterGUI()
    app.run()


if __name__ == "__main__":
    main()
