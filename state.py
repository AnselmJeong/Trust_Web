import reflex as rx
import datetime
import json
from pathlib import Path
import numpy as np
import random
from typing import List, Dict, Optional, Callable, Any

# Game constants
PROLIFERATION_FACTOR = 2
INITIAL_BALANCE = 20
NUM_ROUNDS = 7


class GameState(rx.State):
    """State for the trust game experiment."""

    # Authentication state
    user_email: str = ""
    password: str = ""
    is_authenticated: bool = False
    auth_error: str = ""

    # Game state
    current_section: int = 0  # 0: Instructions, 1: Player B, 2: Player A
    current_round: int = 1
    is_ready: bool = False

    # Player B section state
    player_b_profit: float = 0
    player_a_profit_section1: float = 0
    sent_by_a: int = 0
    amount_to_return: str = "0"  # Must be string for on_change events

    # Player A section state
    player_a_balance: int = INITIAL_BALANCE
    player_a_profit_section2: float = 0
    player_b_profit_section2: float = 0
    amount_to_send: str = "0"  # Must be string for on_change events
    amount_returned: int = 0

    # Game history
    section1_history: List[Dict] = []
    section2_history: List[Dict] = []

    # Player B profile for section 2
    player_b_profile: Optional[Dict] = None

    @rx.event
    def set_user_email(self, value: str) -> None:
        """Set the user email."""
        self.user_email = value

    @rx.event
    def set_password(self, value: str) -> None:
        """Set the user password."""
        self.password = value

    @rx.event
    def set_amount_to_return(self, value: str) -> None:
        """Set the amount to return from string input."""
        try:
            amount = int(value)
            if amount >= 0:
                self.amount_to_return = value
        except ValueError:
            pass

    @rx.event
    def set_amount_to_send(self, value: str) -> None:
        """Set the amount to send from string input."""
        try:
            amount = int(value)
            if amount >= 0:
                self.amount_to_send = value
        except ValueError:
            pass

    @rx.event
    def login(self) -> None:
        """Handle user login."""
        try:
            # For now, just set authenticated to true
            self.is_authenticated = True
            self.auth_error = ""
        except Exception as e:
            self.auth_error = str(e)

    @rx.event
    def register(self) -> None:
        """Handle user registration."""
        try:
            # For now, just set authenticated to true
            self.is_authenticated = True
            self.auth_error = ""
        except Exception as e:
            self.auth_error = str(e)

    @rx.event
    def logout(self) -> None:
        """Handle user logout."""
        self.user_email = ""
        self.password = ""
        self.is_authenticated = False
        self.reset_game_state()

    @rx.event
    def submit_player_b_decision(self) -> None:
        """Handle Player B's decision submission."""
        try:
            amount = int(self.amount_to_return)
            if amount < 0 or amount > self.sent_by_a * PROLIFERATION_FACTOR:
                return

            # Calculate profits
            received_amount = self.sent_by_a * PROLIFERATION_FACTOR
            player_b_profit = received_amount - amount
            player_a_profit = amount - self.sent_by_a

            # Update cumulative profits
            self.player_b_profit += player_b_profit
            self.player_a_profit_section1 += player_a_profit

            # Record round
            round_data = {
                "round": self.current_round,
                "sent_by_a": self.sent_by_a,
                "amount_returned": amount,
                "player_b_profit": player_b_profit,
                "player_a_profit": player_a_profit,
                "timestamp": datetime.datetime.now().isoformat(),
            }
            self.section1_history.append(round_data)

            # Move to next round or section
            if self.current_round < NUM_ROUNDS:
                self.current_round += 1
                self.simulate_player_a_decision()
                self.amount_to_return = "0"
            else:
                self.current_section = 2
                self.current_round = 1
                self.select_player_b_profile()

        except ValueError:
            pass

    @rx.event
    def submit_player_a_decision(self) -> None:
        """Handle Player A's decision submission."""
        try:
            amount = int(self.amount_to_send)
            if amount < 0 or amount > self.player_a_balance // 2:
                return

            # Calculate Player B's return
            self.amount_returned = self.calculate_player_b_return(amount)

            # Calculate profits
            player_a_profit = self.amount_returned - amount
            player_b_profit = (amount * PROLIFERATION_FACTOR) - self.amount_returned

            # Update balances and profits
            self.player_a_balance = self.player_a_balance - amount + self.amount_returned
            self.player_a_profit_section2 += player_a_profit
            self.player_b_profit_section2 += player_b_profit

            # Record round
            round_data = {
                "round": self.current_round,
                "amount_sent": amount,
                "amount_returned": self.amount_returned,
                "player_a_profit": player_a_profit,
                "player_b_profit": player_b_profit,
                "player_a_balance": self.player_a_balance,
                "timestamp": datetime.datetime.now().isoformat(),
            }
            self.section2_history.append(round_data)

            # Move to next round or end
            if self.current_round < NUM_ROUNDS:
                self.current_round += 1
                self.amount_to_send = "0"
            else:
                self.current_section = 3  # End of experiment

        except ValueError:
            pass

    @rx.event
    def simulate_player_a_decision(self):
        """Simulate Player A's decision for Section 1."""
        max_investment = self.player_a_balance // 2
        self.sent_by_a = random.randint(0, max_investment)

    @rx.event
    def select_player_b_profile(self):
        """Select a random Player B profile for Section 2."""
        profiles = {
            "fair": {
                "base_fairness": 0.5,
                "generosity_bias": 0.1,
                "fairness_variance": 0.1,
                "large_investment_cutoff": 10,
                "large_investment_bias": 0.1,
                "end_game_fairness_drop": 0.1,
            },
            "opportunist": {
                "base_fairness": 0.3,
                "generosity_bias": -0.1,
                "fairness_variance": 0.2,
                "large_investment_cutoff": 5,
                "large_investment_bias": 0.2,
                "end_game_fairness_drop": 0.3,
            },
        }
        self.player_b_profile = random.choice(list(profiles.values()))

    @rx.event
    def calculate_player_b_return(self, amount_sent: int) -> int:
        """Calculate Player B's return amount based on profile."""
        if not self.player_b_profile:
            return 0

        params = self.player_b_profile
        loc_value = params["base_fairness"] + params["generosity_bias"]

        if amount_sent > params["large_investment_cutoff"]:
            loc_value -= params["large_investment_bias"]

        base_return_rate = np.random.normal(loc_value, params["fairness_variance"])
        base_return = (amount_sent * PROLIFERATION_FACTOR) * base_return_rate

        if self.current_round > NUM_ROUNDS * 0.8:
            base_return *= 1 - params["end_game_fairness_drop"]

        max_return = amount_sent * PROLIFERATION_FACTOR
        return min(max(0, round(base_return)), max_return)

    @rx.event
    def mark_ready(self) -> None:
        """Mark user as ready to start the experiment."""
        self.is_ready = True
        self.current_section = 1
        self.current_round = 1
        self.simulate_player_a_decision()

    @rx.event
    def reset_game_state(self):
        """Reset all game state variables."""
        self.current_section = 0
        self.current_round = 1
        self.is_ready = False
        self.player_b_profit = 0
        self.player_a_profit_section1 = 0
        self.sent_by_a = 0
        self.amount_to_return = "0"
        self.player_a_balance = INITIAL_BALANCE
        self.player_a_profit_section2 = 0
        self.player_b_profit_section2 = 0
        self.amount_to_send = "0"
        self.amount_returned = 0
        self.section1_history = []
        self.section2_history = []
        self.player_b_profile = None
