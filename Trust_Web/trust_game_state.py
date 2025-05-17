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

# Load personality profiles from toml file
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
    # current_page는 화면에 비춰질 page의 번호이다.
    # 전체 session의 구성은 아래와 같이 이루어진다. 중간중간에 안내문이 들어가므로 page 번호는 아래와 일치하지 않는다.
    # 1. 로그인 페이지
    # 2. Demographic 기입 페이지
    # 3. 대인관계 설문지
    # 4. 공공재 게임 안내문
    # 5. 공공재 게임
    # 6. 신뢰 게임 안내
    # 7. 신뢰 게임 section 1
    # 8. 신뢰 게임 section 2
    # 9. 종료

    current_page: int = 0

    # current_round는 현재 진행중인 라운드의 번호이다.
    # 공공재, 신뢰 게임에서 한 상대와 총 10번의 round를 진행하게 된다.
    current_round: int = 1

    # current_stage는 신뢰 게임 section 2에서 거래하고 상대의 번호이다.
    # section 2에서 총 5명의 상대와 거래를 진행하게 된다.
    current_stage: int = 0  # 0-4: Stages in Section 2
    is_ready: bool = False
    is_stage_transition: bool = False  # 거래 상대 교체 시 페이지 전환을 위한 플래그

    # Player B state
    # balance는 section이나 stage가 바뀌면 초기화된다.
    # 그러나 round가 바뀔 때는 이전 금액에 누적된다.
    player_b_balance: int = 0  # 수탁자의 현재 잔액
    player_b_current_round_profit: float = 0  # 수탁자가 현재 라운드에서 얻은 이익

    # Player A state
    player_a_balance: int = 0  # 투자자의 현재 잔액
    player_a_current_round_profit: float = 0  # 투자자가 현재 라운드에서 얻은 이익

    # Transaction data
    amount_to_send: int = 0  # 투자자(player_a)가 투자할 금액
    amount_to_return: int = 0  # 수탁자(player_b)가 투자자에게 돌려줄 금액
    message_b: str = ""  # 수탁자(player_b)가 투자자에게 보내는 메시지

    # Game history
    round_history: List[Dict] = []  # 현재 stage에서 진행된 모든 round의 데이터를 저장하는 리스트

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
            self.player_b_current_round_profit = player_b_profit
            self.player_a_current_round_profit = player_a_profit

            # Move to next round or section
            if self.current_round < NUM_ROUNDS:
                self.current_round += 1
                self.simulate_player_a_decision()
                self.amount_to_return = 0
                self.player_a_current_round_profit = 0
                self.player_b_current_round_profit = 0
            else:
                self.current_page = 2  # Move to transition page
                self.current_round = 1
                self.player_a_current_round_profit = 0
                self.player_b_current_round_profit = 0

        except ValueError:
            pass

    @rx.event
    def start_section_1(self) -> None:
        """Mark user as ready to start the experiment."""
        self.is_ready = True
        self.player_a_balance = INITIAL_BALANCE
        self.player_b_balance = 0  # Player B starts with 0 balance in section 1
        self.current_page = 1  # Start Section 1 (Player B)
        self.current_round = 1
        self.player_a_current_round_profit = 0
        self.player_b_current_round_profit = 0
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
        self.player_b_balance = (
            0  # Player B's balance for this AI is reset/not tracked globally here
        )
        self.amount_to_send = 0
        self.amount_to_return = 0
        self.current_page = 3  # Move to Section 2 (Player A)
        self.player_a_current_round_profit = 0
        self.player_b_current_round_profit = 0
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
            self.player_b_balance += (
                player_b_profit  # This AI Player B's balance accumulates per stage
            )
            self.player_a_current_round_profit = player_a_profit
            self.player_b_current_round_profit = player_b_profit

            # Record round
            round_data: Dict[str, Any] = {
                "user_id": self.user_id,
                "stage": self.current_stage,
                "round": self.current_round,
                "personality": self.player_b_personality,
                "amount_sent": self.amount_to_send,
                "amount_returned": self.amount_to_return,
                "player_a_current_round_profit": player_a_profit,
                "player_b_current_round_profit": player_b_profit,
                "ai_message": self.message_b,
                "timestamp": datetime.datetime.now().isoformat(),
            }
            self.round_history.append(round_data)
            save_experiment_data(round_data)

            # Move to next round or stage
            if self.current_round < NUM_ROUNDS:
                self.current_round += 1
                self.amount_to_send = 0
                self.player_a_current_round_profit = 0
                self.player_b_current_round_profit = 0
            else:
                # Move to next stage
                self.current_stage += 1
                if self.current_stage >= len(self.shuffled_profiles):
                    # All stages completed, move to final page
                    self.current_page = 4
                else:
                    # Show stage transition page
                    self.is_stage_transition = True
                # Reset profits for new stage/end of game
                self.player_a_current_round_profit = 0
                self.player_b_current_round_profit = 0

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
        self.player_a_current_round_profit = 0
        self.player_b_current_round_profit = 0
        self.player_b_balance = 0  # Reset AI player B's balance for the new stage
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
        self.player_a_current_round_profit = 0
        self.player_b_current_round_profit = 0

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
