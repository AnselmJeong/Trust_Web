import datetime
import random
import numpy as np
import toml
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple

import reflex as rx
from .firebase_config import sign_in_with_email_and_password, create_user_with_email_and_password
from .firebase_db import save_experiment_data

NUM_ROUNDS = 10
PROLIFERATION_FACTOR = 3
INITIAL_BALANCE = 10

# Load personality profiles
PROFILES_PATH: Path = Path(__file__).parent / "profiles" / "personalities.toml"
with open(PROFILES_PATH, "r") as f:
    PERSONALITY_PROFILES: Dict[str, Any] = toml.load(f)


class TrustGameState(rx.State):
    """State for the trust game experiment."""

    # Authentication state
    user_email: str = ""
    password: str = ""
    confirm_password: str = ""
    is_authenticated: bool = False
    auth_error: str = ""
    user_id: str = ""

    # Game state
    current_page: int = 0  # 0: Instructions, 1: Section 1 (Player B), 2: Transition, 3: Section 2 (Player A), 4: End
    current_round: int = 1
    current_stage: int = 0  # 0-4: Stages in Section 2
    is_ready: bool = False
    is_stage_transition: bool = False  # Flag for stage transition page

    # Player B state
    player_b_balance: int = 0
    player_b_profit: float = 0

    # Player A state
    player_a_balance: int = 0
    player_a_profit: float = 0

    # Transaction data
    amount_to_send: int = 0
    amount_to_return: int = 0
    message_b: str = ""

    # Game history
    round_history: List[Dict] = []  # History for current stage

    # Player B profiles for section 2
    shuffled_profiles: List[Tuple[str, Dict]] = []  # List of (personality, profile) tuples
    player_b_personality: str = ""
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
    def set_confirm_password(self, value: str) -> None:
        """Set the confirm password."""
        self.confirm_password = value

    @rx.event
    def set_amount_to_return(self, value: str) -> None:
        """Set the amount to return from string input."""
        try:
            amount = int(value)
            if amount > 0 and amount <= self.received_amount:
                self.amount_to_return = int(value)
            else:
                raise ValueError(
                    "Please enter positive amount less than or equal to the amount you received"
                )
        except ValueError:
            raise ValueError("Please enter a valid integer value")

    @rx.event
    def set_amount_to_send(self, value: str) -> None:
        """Set the amount to send from string input."""
        try:
            amount = int(value)
            if amount > 0 and amount <= self.max_send_amount:
                self.amount_to_send = int(value)
            else:
                raise ValueError(
                    "Please enter positive amount less than or equal to half of your balance"
                )
        except ValueError:
            raise ValueError("Please enter a valid integer value")

    # ========================== Transaction ==========================
    @rx.event
    def simulate_player_a_decision(self) -> None:
        """Simulate Player A's decision for Section 1."""
        print(f"initial_balance: {self.player_a_balance}")
        print(f"max_send_amount: {self.max_send_amount}")
        self.amount_to_send = random.randint(1, self.max_send_amount)

    @rx.event
    def submit_player_b_decision(self) -> None:
        """Handle Player B's decision submission.
        This function is executed when a human participant plays as player_b in the first section.
        """
        try:
            # Calculate profits
            player_b_profit: int = self.received_amount - self.amount_to_return
            player_a_profit: int = self.amount_to_return - self.amount_to_send

            # Update balances and profits
            self.player_b_balance += player_b_profit  # Update Player B's balance
            self.player_a_balance += player_a_profit

            # Move to next round or section
            if self.current_round < NUM_ROUNDS:
                self.current_round += 1
                self.simulate_player_a_decision()
                self.amount_to_return = 0
            else:
                self.current_page = 2  # Move to transition page
                self.current_round = 1

        except ValueError:
            pass

    @rx.event
    def start_section_1(self) -> None:
        """Mark user as ready to start the experiment."""
        self.is_ready = True
        self.player_a_balance = INITIAL_BALANCE
        self.current_page = 1  # Start Section 1 (Player B)
        self.current_round = 1
        self.simulate_player_a_decision()

    @rx.event
    def start_section_2(self) -> None:
        """Start Section 2 after the transition page."""
        # Shuffle the profiles and store them
        profiles = list(PERSONALITY_PROFILES.items())
        random.shuffle(profiles)
        self.shuffled_profiles = profiles

        # Initialize first stage
        self.current_stage = 0
        self.current_round = 1
        self.player_a_balance = INITIAL_BALANCE
        self.amount_to_send = 0
        self.amount_to_return = 0
        self.current_page = 3  # Move to Section 2 (Player A)
        self.select_player_b_profile()

    @rx.event
    def select_player_b_profile(self) -> None:
        """Select the Player B profile for the current stage."""
        self.player_b_personality, self.player_b_profile = self.shuffled_profiles[
            self.current_stage
        ]

    @rx.event
    def main_algorithm(self) -> None:
        """
        The main game logic for Section 2.
        Handle Player A's decision submission.
        This function is executed when a human participant plays as player_a in the second section.
        """
        try:
            # Calculate Player B's return amount based on the profile
            self.amount_to_return = self.calculate_player_b_return(self.amount_to_send)

            # for debugging
            print(f"current_personality: {self.player_b_personality}")
            print(f"amount_sent: {self.amount_to_send}")
            print(f"amount_returned: {self.amount_to_return}")

            # Calculate profits
            player_a_profit: int = self.amount_to_return - self.amount_to_send
            player_b_profit: int = self.received_amount - self.amount_to_return

            # Update balances and profits
            self.player_a_balance += player_a_profit
            self.player_b_balance += player_b_profit

            # Record round
            round_data: Dict[str, Any] = {
                "user_id": self.user_id,
                "stage": self.current_stage,
                "round": self.current_round,
                "personality": self.player_b_personality,
                "amount_sent": self.amount_to_send,
                "amount_returned": self.amount_to_return,
                "human_profit": player_a_profit,
                "ai_profit": player_b_profit,
                "ai_message": self.message_b,
                "timestamp": datetime.datetime.now().isoformat(),
            }
            self.round_history.append(round_data)
            save_experiment_data(round_data)

            # Move to next round or stage
            if self.current_round < NUM_ROUNDS:
                self.current_round += 1
                self.amount_to_send = 0
            else:
                # Move to next stage
                self.current_stage += 1
                if self.current_stage >= len(self.shuffled_profiles):
                    # All stages completed, move to final page
                    self.current_page = 4
                else:
                    # Show stage transition page
                    self.is_stage_transition = True

        except ValueError:
            pass

    @rx.event
    def calculate_player_b_return(self) -> int:
        """Calculate Player B's return amount based on profile."""

        if not self.player_b_profile:
            return 0

        params: Dict[str, float] = self.player_b_profile["parameters"]
        loc_value: float = params["base_fairness"] + params["generosity_bias"]

        if self.amount_to_send > params["large_investment_cutoff"]:
            loc_value -= params["large_investment_bias"]

        base_return_rate: float = np.random.normal(loc_value, params["fairness_variance"])
        base_return: float = self.received_amount * base_return_rate

        if self.current_round > NUM_ROUNDS * 0.8:
            base_return *= 1 - params["end_game_fairness_drop"]

        max_return: int = self.received_amount
        return min(max(0, round(base_return)), max_return)

    @rx.event
    def start_next_stage(self) -> None:
        """Start the next stage after the transition page."""
        self.is_stage_transition = False
        self.current_round = 1
        self.amount_to_send = 0
        self.round_history = []  # Initialize history for new stage
        self.select_player_b_profile()

    @rx.event
    def reset_game_state(self) -> None:
        """Reset all game state variables."""
        self.current_page = 0
        self.current_round = 1
        self.current_stage = 0
        self.is_ready = False
        self.is_stage_transition = False

        self.amount_to_send = 0
        self.amount_to_return = 0

        self.player_a_balance = INITIAL_BALANCE
        self.player_b_balance = 0
        self.player_a_profit = 0
        self.player_b_profit = 0

        self.round_history = []
        self.shuffled_profiles = []
        self.player_b_profile = None

    @rx.var
    def received_amount(self) -> int:
        return self.amount_to_send * PROLIFERATION_FACTOR

    @rx.var
    def progress_percent(self) -> float:
        return (self.current_round - 1) / NUM_ROUNDS * 100

    @rx.var
    def max_send_amount(self) -> int:
        return self.player_a_balance // 2

    @rx.var
    def round_str(self) -> str:
        return f"Round {self.current_round} / {NUM_ROUNDS}"

    # ================= Authentication =================

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

            # Check if passwords match
            if self.password != self.confirm_password:
                self.auth_error = "Passwords do not match"
                return

            user = create_user_with_email_and_password(self.user_email, self.password)
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
