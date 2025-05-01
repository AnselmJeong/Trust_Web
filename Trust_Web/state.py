import datetime
import random
import numpy as np
import toml
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple

import reflex as rx
from .firebase_config import (
    sign_in_with_email_and_password,
    create_user_with_email_and_password,
    save_experiment_data,
)

NUM_ROUNDS = 10
PROLIFERATION_FACTOR = 3
INITIAL_BALANCE = 10

# Load personality profiles
PROFILES_PATH: Path = Path(__file__).parent / "profiles" / "personalities.toml"
with open(PROFILES_PATH, "r") as f:
    PERSONALITY_PROFILES: Dict[str, Any] = toml.load(f)


class GameState(rx.State):
    """State for the trust game experiment."""

    # Authentication state
    user_email: str = ""
    password: str = ""
    is_authenticated: bool = False
    auth_error: str = ""
    user_id: str = ""

    # Game state
    current_section: int = 0  # 0: Instructions, 1: Player B, 2: Player A
    current_round: int = 1
    is_ready: bool = False

    # Player B section state
    player_b_profit: float = 0
    player_a_profit_section1: float = 0
    sent_by_a: int = 0
    amount_to_return: int = 0
    message_b: str = ""
    # Player A section state
    player_a_balance: int = INITIAL_BALANCE
    player_a_profit_section2: float = 0
    player_b_profit_section2: float = 0
    amount_to_send: int = 0
    amount_returned: int = 0

    # Game history
    section1_history: List[Dict] = []
    section2_history: List[Dict] = []

    # Player B profile for section 2
    personality: str = ""
    player_b_profile: Optional[Dict] = None

    @rx.var
    def received_amount(self) -> int:
        return self.sent_by_a * PROLIFERATION_FACTOR

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
            if amount > 0 and amount <= self.sent_by_a * PROLIFERATION_FACTOR:
                self.amount_to_return = int(value)
            else:
                raise ValueError(
                    "Please enter positive amount less than or equal to the amount you earned"
                )
        except ValueError:
            raise ValueError("Please enter a valid integer value")

    @rx.event
    def set_amount_to_send(self, value: str) -> None:
        """Set the amount to send from string input."""
        try:
            amount = int(value)
            if amount > 0 and amount <= self.player_a_balance // 2:
                self.amount_to_send = int(value)
            else:
                raise ValueError(
                    "Please enter positive amount less than or equal to half of your balance"
                )
        except ValueError:
            raise ValueError("Please enter a valid integer value")

    @rx.event
    def login(self) -> None:
        """Handle user login using Firebase."""
        try:
            if not self.user_email or not self.password:
                self.auth_error = "Please enter both email and password"
                return

            user = sign_in_with_email_and_password(self.user_email, self.password)
            # The response contains 'localId' instead of 'uid'
            self.user_id = user.get("localId")
            self.is_authenticated = True
            self.auth_error = ""

        except Exception as e:
            self.auth_error = str(e)

    @rx.event
    def register(self) -> None:
        """Handle user registration using Firebase."""
        try:
            if not self.user_email or not self.password:
                self.auth_error = "Please enter both email and password"
                return

            user = create_user_with_email_and_password(self.user_email, self.password)
            # The response contains 'localId' instead of 'uid'
            self.user_id = user.get("localId")
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
        self.user_id = ""
        self.reset_game_state()

    @rx.event
    def submit_player_b_decision(self) -> None:
        """Handle Player B's decision submission."""
        try:
            amount = int(self.amount_to_return)
            if amount < 0 or amount > self.sent_by_a * PROLIFERATION_FACTOR:
                return

            # Calculate profits
            received_amount: int = self.sent_by_a * PROLIFERATION_FACTOR
            player_b_profit: int = received_amount - amount
            player_a_profit: int = amount - self.sent_by_a

            # Update cumulative profits
            self.player_b_profit += player_b_profit
            self.player_a_profit_section1 += player_a_profit

            # Record round
            round_data: Dict[str, Any] = {
                "user_id": self.user_id,
                "round": self.current_round,
                "sent_by_a": self.sent_by_a,
                "amount_returned": amount,
                "player_b_profit": player_b_profit,
                "player_a_profit": player_a_profit,
                "timestamp": datetime.datetime.now().isoformat(),
            }
            self.section1_history.append(round_data)
            save_experiment_data(round_data)

            # Move to next round or section
            if self.current_round < NUM_ROUNDS:
                self.current_round += 1
                self.simulate_player_a_decision()
                self.amount_to_return = 0
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
            # If amount_str is provided, use it directly
            amount = self.amount_to_send

            if amount < 0 or amount > self.player_a_balance // 2:
                return

            # Calculate Player B's return
            self.amount_returned = self.calculate_player_b_return(amount)
            print(f"current_personality: {self.personality}")
            print(f"amount_sent: {amount}")
            print(f"amount_returned: {self.amount_returned}")

            # implement the logic to call LLM
            description = self.player_b_profile["description"]

            self.message_b = "Thank you..."

            # Calculate profits
            player_a_profit: int = self.amount_returned - amount
            player_b_profit: int = (amount * PROLIFERATION_FACTOR) - self.amount_returned

            # Update balances and profits
            self.player_a_balance = self.player_a_balance - amount + self.amount_returned
            self.player_a_profit_section2 += player_a_profit
            self.player_b_profit_section2 += player_b_profit

            # Record round
            round_data: Dict[str, Any] = {
                "user_id": self.user_id,
                "round": self.current_round,
                "amount_sent": amount,
                "amount_returned": self.amount_returned,
                "player_a_profit": player_a_profit,
                "player_b_profit": player_b_profit,
                "player_a_balance": self.player_a_balance,
                "message_b": self.message_b,
                "timestamp": datetime.datetime.now().isoformat(),
            }
            self.section2_history.append(round_data)
            save_experiment_data(round_data)

            # Move to next round or end
            if self.current_round < NUM_ROUNDS:
                self.current_round += 1
                self.amount_to_send = 0
            else:
                self.current_section = 3  # End of experiment

        except ValueError:
            pass

    @rx.event
    def simulate_player_a_decision(self) -> None:
        """Simulate Player A's decision for Section 1."""
        max_investment: int = self.player_a_balance // 2
        self.sent_by_a = random.randint(0, max_investment)

    @rx.event
    def select_player_b_profile(self) -> None:
        """Select a random Player B profile for Section 2."""
        # Convert TOML data to list of profiles
        profiles: List[Tuple[str, Dict[str, float]]] = list(PERSONALITY_PROFILES.items())
        personality, player_b_profile = random.choice(profiles)
        self.player_b_profile = player_b_profile
        self.personality = personality

    @rx.event
    def calculate_player_b_return(self, amount_sent: int) -> int:
        """Calculate Player B's return amount based on profile."""

        if not self.player_b_profile:
            return 0

        params: Dict[str, float] = self.player_b_profile["parameters"]
        loc_value: float = params["base_fairness"] + params["generosity_bias"]

        if amount_sent > params["large_investment_cutoff"]:
            loc_value -= params["large_investment_bias"]

        base_return_rate: float = np.random.normal(loc_value, params["fairness_variance"])
        base_return: float = (amount_sent * PROLIFERATION_FACTOR) * base_return_rate

        if self.current_round > NUM_ROUNDS * 0.8:
            base_return *= 1 - params["end_game_fairness_drop"]

        max_return: int = amount_sent * PROLIFERATION_FACTOR
        return min(max(0, round(base_return)), max_return)

    @rx.event
    def mark_ready(self) -> None:
        """Mark user as ready to start the experiment."""
        self.is_ready = True
        self.current_section = 1
        self.current_round = 1
        self.simulate_player_a_decision()

    @rx.event
    def reset_game_state(self) -> None:
        """Reset all game state variables."""
        self.current_section = 0
        self.current_round = 1
        self.is_ready = False
        self.player_b_profit = 0
        self.player_a_profit_section1 = 0
        self.sent_by_a = 0
        self.amount_to_return = 0
        self.player_a_balance = INITIAL_BALANCE
        self.player_a_profit_section2 = 0
        self.player_b_profit_section2 = 0
        self.amount_to_send = 0
        self.amount_returned = 0
        self.section1_history = []
        self.section2_history = []
        self.player_b_profile = None

    @rx.var
    def progress_percent(self) -> float:
        return (self.current_round - 1) / NUM_ROUNDS * 100

    @rx.var
    def max_send_amount(self) -> int:
        return self.player_a_balance // 2

    @rx.var
    def round_str(self) -> str:
        return f"Round {self.current_round} / {NUM_ROUNDS}"
