import datetime
import random
import numpy as np
import toml
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple

import reflex as rx
from .firebase_db import save_experiment_data
# from Trust_Web.authentication import AuthState
# from reflex.utils import get_value
# from .authentication import AuthState # Removed

NUM_ROUNDS = 3  # test 용으로 원래는 10
PROLIFERATION_FACTOR = 3
INITIAL_BALANCE = 10

# Load personality profiles from toml file
PROFILES_PATH: Path = Path(__file__).parent / "profiles" / "personalities.toml"
with open(PROFILES_PATH, "r") as f:
    PERSONALITY_PROFILES: Dict[str, Any] = toml.load(f)


class TrustGameState(rx.State):
    """State for the trust game experiment."""

    # Game state
    # current_page는 화면에 비춰질 page의 번호이다.
    # 전체 session의 구성은 아래와 같이 이루어진다. 중간중간에 안내문이 들어가므로 page 번호는 아래와 일치하지 않는다.
    # 0. Questionnaire Page (New)
    # 1. Instructions (공공재 게임 안내문) (was 0)
    # 2. Public Goods Game (was 1)
    # 3. Section 1 (Trust Game - Player B) (was 2)
    # 4. Section Transition (between Trust Game Section 1 and 2) (was 3)
    # 5. Section 2 (Trust Game - Player A) (was 4)
    # 6. Trust Game Instructions (신뢰 게임 안내) (was 6, remains 6)
    # 7. Final Page (new explicit page number)

    # current_round는 현재 진행중인 라운드의 번호이다.
    # 공공재, 신뢰 게임에서 한 상대와 총 10번의 round를 진행하게 된다.
    current_round: int = 1

    # current_stage는 신뢰 게임 section 2에서 거래하고 상대의 번호이다.
    # section 2에서 총 5명의 상대와 거래를 진행하게 된다.
    current_stage: int = 0  # 0-4: Stages in Section 2
    is_ready: bool = False
    is_stage_transition: bool = False  # 거래 상대 교체 시 페이지 전환을 위한 플래그
    is_decision_submitted: bool = False

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

    current_section: str = "section1"  # "section1" or "section2"

    is_last_stage: bool = False

    game_began_at: str = ""

    user_id: str = ""
    user_email: str = ""

    @rx.event
    def set_amount_to_return(self, value: str) -> None:
        """Set the amount to return from string input."""
        try:
            amount = int(value)
            if amount > 0 and amount <= self.received_amount:
                self.amount_to_return = int(value)
            else:
                raise ValueError("Please enter positive amount <= received amount")
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
                raise ValueError("Please enter positive amount <= half of balance")
        except ValueError:
            raise ValueError("Please enter a valid integer value")

    @rx.event
    def set_user_identity(self, user_id: str, user_email: str):
        """Sets the user ID and email for the trust game state."""
        self.user_id = user_id
        self.user_email = user_email

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
            self.player_b_current_round_profit = self.received_amount - self.amount_to_return
            self.player_a_current_round_profit = self.amount_to_return - self.amount_to_send
            self.player_b_balance += self.player_b_current_round_profit
            self.player_a_balance += self.player_a_current_round_profit
            self.is_decision_submitted = True
            # Section 1: 실험 데이터 저장
            if self.current_section == "section1":
                transaction = {
                    "user_id": self.user_id,
                    "user_email": self.user_email,
                    "game_name": "trust game",
                    "section_num": 1,
                    "round": self.get_value("current_round"),
                    "amount_sent": self.get_value("amount_to_send"),
                    "amount_returned": self.get_value("amount_to_return"),
                    "human_profit": self.get_value("amount_to_send") - self.get_value("amount_to_return"),
                    "player_b_profit": self.get_value("amount_to_return") - (self.get_value("amount_to_send") * PROLIFERATION_FACTOR),
                    "game_began_at": self.get_value("game_began_at"),
                }
                save_experiment_data(self.user_id, transaction)
            # Move to next round or section
            # 다음 라운드로 이동은 별도 이벤트(go_to_next_round)에서 처리
            pass
        except ValueError:
            pass

    @rx.event
    def go_to_next_round(self) -> None:
        self.is_decision_submitted = False
        if self.current_round < NUM_ROUNDS:
            self.current_round += 1
            self.simulate_player_a_decision()
            self.amount_to_return = 0
            self.player_a_current_round_profit = 0
            self.player_b_current_round_profit = 0
        else:
            self.current_round = 1
            self.player_a_current_round_profit = 0
            self.player_b_current_round_profit = 0
            if self.current_section == "section2":
                self.current_stage += 1
                if self.current_stage == len(self.shuffled_profiles):
                    self.is_last_stage = True
                else:
                    self.is_last_stage = False
                return self.proceed_to_stage_transition()
            else:
                self.is_last_stage = False
                return self.proceed_to_section_transition()

    @rx.event
    def start_section_1(self) -> None:
        """Mark user as ready to start the experiment section 1 (Player B Trust Game)."""
        print("[DEBUG] Section 1 start")
        import datetime
        self.game_began_at = datetime.datetime.now().isoformat()
        return self.proceed_to_section1()

    @rx.event
    def start_section_2(self) -> None:
        """Start Section 2 after the transition page."""
        print("[DEBUG] Section 2 start")
        import datetime
        self.game_began_at = datetime.datetime.now().isoformat()
        return self.proceed_to_section2()

    @rx.event
    def select_player_b_profile(self) -> None:
        """Select the Player B profile for the current stage."""
        self.player_b_personality, self.player_b_profile = self.shuffled_profiles[self.current_stage]

    @rx.event
    def main_algorithm(self) -> None:
        """
        The main game logic for Section 2.
        Handle Player A's decision submission.
        This function is executed when a human participant plays as player_a in the second section.
        """
        try:
            # 매번 AuthState에서 값을 복사 (지연 import로 circular import 방지)
            from Trust_Web.authentication import AuthState
            self.set_user_identity(str(AuthState.user_id), str(AuthState.user_email))

            # Calculate Player B's return amount based on the profile
            self.amount_to_return = self.calculate_player_b_return()

            # Calculate profits
            player_a_profit: int = self.amount_to_return - self.amount_to_send
            player_b_profit: int = self.received_amount - self.amount_to_return

            # Update balances and profits
            self.player_a_balance += player_a_profit
            self.player_b_balance += player_b_profit
            self.player_a_current_round_profit = player_a_profit
            self.player_b_current_round_profit = player_b_profit

            # Record round
            round_data: Dict[str, Any] = {
                "user_email": self.user_email,
                "user_id_field": self.user_id,
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

            # Section 2: 실험 데이터 저장
            if self.current_section == "section2":
                transaction = {
                    "user_id": self.user_id,
                    "user_email": self.user_email,
                    "game_name": "trust game",
                    "section_num": 2,
                    "stage_num": self.get_value("current_stage"),
                    "round": self.get_value("current_round"),
                    "player_b_profile": self.get_value("player_b_profile"),
                    "amount_sent": self.get_value("amount_to_send"),
                    "amount_returned": self.get_value("amount_to_return"),
                    "message": self.get_value("message_b"),
                    "human_profit": player_a_profit,
                    "player_b_profit": player_b_profit,
                    "game_began_at": self.get_value("game_began_at"),
                }
                save_experiment_data(self.user_id, transaction)

            self.is_decision_submitted = True
            # 결과만 보여주고, 라운드/스테이지 이동은 go_to_next_round에서만 처리
            return None
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
        self.is_decision_submitted = False
        self.is_stage_transition = False
        self.current_round = 1
        self.amount_to_send = 0
        self.player_a_current_round_profit = 0
        self.player_b_current_round_profit = 0
        self.player_b_balance = 0
        self.select_player_b_profile()
        return rx.redirect("/app/section2")

    @rx.event
    def reset_game_state(self) -> None:
        self.is_decision_submitted = False
        self.is_last_stage = False
        print("[TRUST_GAME_STATE] reset_game_state called")
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

    # @rx.event
    # def go_to_trust_game_instructions(self):
    #     """Navigate to trust game instructions page."""
    #     return rx.redirect("/app/instructions?game=section1")

    @rx.var
    def player_a_total_profit_in_section2(self) -> int:
        """Calculates the total profit for Player A in Section 2 so far."""
        return self.player_a_balance - INITIAL_BALANCE

    @rx.event
    def proceed_to_section1(self):
        self.current_section = "section1"
        self.is_decision_submitted = False
        self.is_ready = True
        self.player_a_balance = INITIAL_BALANCE
        self.player_b_balance = 0  # Player B starts with 0 balance in section 1
        self.current_round = 1
        self.player_a_current_round_profit = 0
        self.player_b_current_round_profit = 0
        self.simulate_player_a_decision()
        self.is_last_stage = False
        return rx.redirect("/app/section1")

    @rx.event
    def proceed_to_section_transition(self):
        """Navigate to section transition page."""
        # self.current_round = 1
        # self.player_a_current_round_profit = 0
        # self.player_b_current_round_profit = 0
        return rx.redirect("/app/instructions?game=section2")

    @rx.event
    def proceed_to_section2(self):
        self.current_section = "section2"
        self.is_decision_submitted = False
        # Shuffle the profiles and store them
        profiles = list(PERSONALITY_PROFILES.items())
        random.shuffle(profiles)
        self.shuffled_profiles = profiles
        print(f"[DEBUG] proceed_to_section2: shuffled_profiles={len(self.shuffled_profiles)}")
        # Initialize first stage (start_next_stage의 stage 초기화 코드 복사)
        self.is_stage_transition = False
        self.current_stage = 0
        self.current_round = 1
        self.amount_to_send = 0
        self.player_a_current_round_profit = 0
        self.player_b_current_round_profit = 0
        self.player_b_balance = 0
        self.round_history = []
        self.select_player_b_profile()
        self.player_a_balance = INITIAL_BALANCE
        self.amount_to_return = 0
        self.is_last_stage = False
        return rx.redirect("/app/section2")

    @rx.event
    def proceed_to_stage_transition(self):
        """Navigate to stage transition page."""
        self.is_stage_transition = True
        return rx.redirect("/app/stage-transition")

    @rx.var
    def stage_total_invested(self) -> int:
        # Sum of amount_sent for the current stage
        return sum(
            r.get("amount_sent", 0)
            for r in self.round_history
            if r.get("stage") == self.current_stage - 1  # stage_transition is shown after stage increment
        )

    @rx.var
    def stage_total_returned(self) -> int:
        # Sum of amount_returned for the current stage
        return sum(r.get("amount_returned", 0) for r in self.round_history if r.get("stage") == self.current_stage - 1)

    @rx.var
    def stage_net_profit(self) -> int:
        # Net profit for player A in the stage
        return sum(
            r.get("player_a_current_round_profit", 0)
            for r in self.round_history
            if r.get("stage") == self.current_stage - 1
        )

    @rx.var
    def stage_end_balance(self) -> int:
        # Player A's balance at the end of the stage (after last round)
        # This is just the current balance after the stage, so use player_a_balance
        return self.player_a_balance

    @rx.var
    def all_stages_total_invested(self) -> list:
        # List of total invested per stage
        if not self.shuffled_profiles:
            return []
        num_stages = len(self.shuffled_profiles)
        return [
            sum(r.get("amount_sent", 0) for r in self.round_history if r.get("stage") == i) for i in range(num_stages)
        ]

    @rx.var
    def all_stages_total_returned(self) -> list:
        # List of total returned per stage
        if not self.shuffled_profiles:
            return []
        num_stages = len(self.shuffled_profiles)
        return [
            sum(r.get("amount_returned", 0) for r in self.round_history if r.get("stage") == i)
            for i in range(num_stages)
        ]

    @rx.var
    def all_stages_net_profit(self) -> list:
        # List of net profit per stage
        if not self.shuffled_profiles:
            return []
        num_stages = len(self.shuffled_profiles)
        return [
            sum(r.get("player_a_current_round_profit", 0) for r in self.round_history if r.get("stage") == i)
            for i in range(num_stages)
        ]

    @rx.var
    def all_stages_end_balance(self) -> list:
        # List of end balance per stage (cumulative)
        if not self.shuffled_profiles:
            return []
        num_stages = len(self.shuffled_profiles)
        balances = []
        running_balance = self.player_a_balance - sum(self.all_stages_net_profit)  # back-calculate initial
        for i in range(num_stages):
            running_balance += self.all_stages_net_profit[i]
            balances.append(running_balance)
        return balances
