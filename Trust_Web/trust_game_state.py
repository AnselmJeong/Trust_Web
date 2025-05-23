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
    player_b_current_round_payoff: float = 0  # 수탁자가 현재 라운드에서 얻은 이익

    # Player A state
    player_a_balance: int = 0  # 투자자의 현재 잔액
    player_a_current_round_payoff: float = 0  # 투자자가 현재 라운드에서 얻은 이익

    # Transaction data
    amount_to_send: int = 0  # 투자자(player_a)가 투자할 금액
    amount_to_return: int = 0  # 수탁자(player_b)가 투자자에게 돌려줄 금액
    message_b: str = ""  # 수탁자(player_b)가 투자자에게 보내는 메시지

    # Game history
    round_history: List[
        Dict
    ] = []  # 현재 stage에서 진행된 모든 round의 데이터를 저장하는 리스트

    # Player B profiles for section 2
    shuffled_profiles: List[
        Tuple[str, Dict]
    ] = []  # List of (personality, profile) tuples
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
        print(
            f"[DEBUG] set_user_identity called with: id='{user_id}', email='{user_email}'"
        )
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
            self.player_b_current_round_payoff = (
                self.received_amount - self.amount_to_return
            )
            self.player_a_current_round_payoff = (
                self.amount_to_return - self.amount_to_send
            )
            self.player_b_balance += self.player_b_current_round_payoff
            self.player_a_balance += self.player_a_current_round_payoff
            self.is_decision_submitted = True
            # Section 1: 실험 데이터 저장
            if self.current_section == "section1":
                transaction = {
                    "user_id": self.user_id,
                    "user_email": self.user_email,
                    # "game_name": "trust_game", # Added by helper
                    # "section_num": 1, # Added by helper
                    "round": self.current_round,
                    "amount_sent": self.amount_to_send,
                    "amount_returned": self.amount_to_return,
                    "player_a_payoff": self.player_a_current_round_payoff,
                    "player_a_balance": self.player_a_balance,
                    "player_b_payoff": self.player_b_current_round_payoff,
                    "player_b_balance": self.player_b_balance,
                    "game_began_at": self.game_began_at,
                }
                self._save_trust_game_round_data(
                    section_num=1,
                    stage_num=0, # Section 1 can be considered stage 0
                    round_num=self.current_round,
                    transaction_data=transaction
                )
            # Move to next round or section
            # 다음 라운드로 이동은 별도 이벤트(go_to_next_round)에서 처리
            pass
        except ValueError:
            pass

    def _reset_round_variables(self):
        """Resets variables at the beginning of each round."""
        self.is_decision_submitted = False
        self.amount_to_return = 0
        self.player_a_current_round_payoff = 0
        self.player_b_current_round_payoff = 0
        # self.message_b = "" # Reset message if applicable, currently seems to be set by AI in S2

    def _reset_stage_variables(self):
        """Resets variables for a new stage (applies to Section 2)."""
        self._reset_round_variables()
        self.current_round = 1
        self.amount_to_send = 0 # Player A starts with 0 to send
        self.player_b_balance = 0 # Opponent's balance resets per stage
        # self.round_history = [] # Round history is for the entire section 2, not per stage

    def _reset_section_balances(self):
        """Resets player balances for a new section."""
        self.player_a_balance = INITIAL_BALANCE # Human player's balance
        self.player_b_balance = 0 # Opponent's balance (for Player B in S1, or AI in S2)

    @rx.event
    def go_to_next_round(self) -> None:
        self._reset_round_variables()
        if self.current_round < NUM_ROUNDS:
            self.current_round += 1
            if self.current_section == "section1":
                self.simulate_player_a_decision() # Player A (AI) makes a decision
        else: # End of rounds for the current stage/section
            self.current_round = 1 # Reset for next stage/section logic, though _reset_stage_variables does it too

            if self.current_section == "section1":
                self.is_last_stage = False # Not applicable directly, but good for consistency
                return self.proceed_to_section_transition()
            elif self.current_section == "section2":
                self.current_stage += 1
                if self.current_stage >= len(self.shuffled_profiles): # Use >= for safety
                    self.is_last_stage = True
                    # Potentially redirect to a final summary or results page for section 2
                    # For now, proceed_to_stage_transition will handle the last stage by showing summary
                else:
                    self.is_last_stage = False
                return self.proceed_to_stage_transition()

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
            # 매번 AuthState에서 값을 복사 (지연 import로 circular import 방지)
            # from Trust_Web.authentication import AuthState
            # self.set_user_identity(str(AuthState.user_id), str(AuthState.user_email))
            # 위 코드를 제거하고, 이미 self.user_id/self.user_email이 올바르게 세팅되어 있다고 가정

            # Calculate Player B's return amount based on the profile
            self.amount_to_return = self.calculate_player_b_return()

            # Calculate payoffs
            player_a_payoff: int = self.amount_to_return - self.amount_to_send
            player_b_payoff: int = self.received_amount - self.amount_to_return

            # Update balances and payoffs
            self.player_a_balance += player_a_payoff
            self.player_b_balance += player_b_payoff
            self.player_a_current_round_payoff = player_a_payoff
            self.player_b_current_round_payoff = player_b_payoff

            # Record round
            round_data: Dict[str, Any] = {
                "user_id": self.user_id,
                "user_email": self.user_email,
                "stage": self.current_stage,
                "round": self.current_round,
                "personality": self.player_b_personality,
                "amount_sent": self.amount_to_send,
                "amount_returned": self.amount_to_return,
                "player_a_current_round_payoff": player_a_payoff,
                "player_b_current_round_payoff": player_b_payoff,
                "ai_message": self.message_b,
                "timestamp": datetime.datetime.now().isoformat(),
            }

            self.round_history.append(round_data)

            # Section 2: 실험 데이터 저장
            if self.current_section == "section2":
                transaction = {
                    "user_id": self.user_id,
                    "user_email": self.user_email,
                    # "game_name": "trust_game", # Added by helper
                    # "section_num": 2, # Added by helper
                    "stage_num": self.current_stage,
                    "round": self.current_round,
                    "player_b_profile_name": self.player_b_personality, # Save profile name
                    "player_b_profile_details": self.player_b_profile, # Save full profile
                    "amount_sent": self.amount_to_send,
                    "amount_returned": self.amount_to_return,
                    "message": self.message_b, # AI message to human
                    "human_payoff": player_a_payoff, # Player A is human in S2
                    "human_balance": self.player_a_balance,
                    "player_b_payoff": player_b_payoff, # Player B is AI in S2
                    "player_b_balance": self.player_b_balance,
                    "game_began_at": self.game_began_at,
                }
                self._save_trust_game_round_data(
                    section_num=2,
                    stage_num=self.current_stage,
                    round_num=self.current_round,
                    transaction_data=transaction
                )

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

        base_return_rate: float = np.random.normal(
            loc_value, params["fairness_variance"]
        )
        base_return: float = self.received_amount * base_return_rate

        if self.current_round > NUM_ROUNDS * 0.8:
            base_return *= 1 - params["end_game_fairness_drop"]

        max_return: int = self.received_amount
        return min(max(0, round(base_return)), max_return)

    def _save_trust_game_round_data(self, section_num: int, stage_num: int, round_num: int, transaction_data: Dict[str, Any]):
        """Helper function to save trust game round data."""
        # Common data to be added by this helper if not already in transaction_data by caller
        # However, current transaction_data seems complete enough.
        # transaction_data["game_name"] = "trust_game" # Already handled by save_experiment_data's game_name param
        # transaction_data["section_num"] = section_num # Already handled by save_experiment_data's section_num param

        document_id = f"stage_{stage_num}_round_{round_num}"
        
        save_experiment_data(
            user_id=self.user_id, # Assumes self.user_id is set
            game_name="trust_game", # Explicitly "trust_game"
            data=transaction_data,
            section_num=section_num,
            document_id=document_id,
        )

    @rx.event
    def start_next_stage(self) -> None:
        self._reset_stage_variables() # Resets round vars, current_round, amount_to_send, player_b_balance
        self.is_stage_transition = False
        # self.player_a_balance is preserved across stages in a section
        self.select_player_b_profile()
        return rx.redirect("/app/section2")

    @rx.event
    def reset_game_state(self) -> None:
        self._reset_stage_variables() # Resets most per-round/stage vars
        self._reset_section_balances() # Resets player_a_balance to initial, player_b_balance to 0
        
        self.is_last_stage = False
        print("[TRUST_GAME_STATE] reset_game_state called")
        self.current_stage = 0
        self.is_ready = False # Should be set true when a section begins
        self.is_stage_transition = False
        self.round_history = [] # Clear history for a full reset
        self.shuffled_profiles = []
        self.player_b_profile = None
        self.player_b_personality = ""
        self.current_section = "section1" # Default to section1 on full reset
        self.game_began_at = ""

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
    def player_a_total_payoff_in_section2(self) -> int:
        """Calculates the total payoff for Player A in Section 2 so far."""
        return self.player_a_balance - INITIAL_BALANCE

    @rx.event
    def proceed_to_section1(self):
        self.current_section = "section1"
        self._reset_section_balances() # Resets player_a_balance to INITIAL_BALANCE, player_b_balance to 0
        self._reset_stage_variables() # Resets round vars, current_round to 1, amount_to_send to 0
                                      # player_b_balance is already 0 from _reset_section_balances
        self.is_ready = True
        self.simulate_player_a_decision() # AI (Player A) makes a decision
        self.is_last_stage = False # Not applicable to section 1 structure
        self.round_history = [] # Clear history for section 1
        return rx.redirect("/app/section1")

    @rx.event
    def proceed_to_section_transition(self):
        """Navigate to section transition page (instructions for section 2)."""
        # No specific state changes here usually, just navigation.
        # Balances are reset when section 2 actually starts.
        return rx.redirect("/app/instructions?game=section2")

    @rx.event
    def proceed_to_section2(self):
        self.current_section = "section2"
        self._reset_section_balances() # Human (Player A) balance reset, AI (Player B) balance to 0
        self._reset_stage_variables()  # Resets round vars, current_round to 1, amount_to_send to 0 etc.
        
        self.is_ready = True # Mark as ready for section 2
        self.current_stage = 0 # Start from the first AI opponent
        self.is_stage_transition = False
        self.is_last_stage = False
        self.round_history = [] # Clear history for section 2

        # Shuffle the profiles and store them
        profiles = list(PERSONALITY_PROFILES.items())
        random.shuffle(profiles)
        self.shuffled_profiles = profiles
        print(
            f"[DEBUG] proceed_to_section2: shuffled_profiles={len(self.shuffled_profiles)}"
        )
        if not self.shuffled_profiles: # Handle case of no profiles
             print("[ERROR] No personality profiles loaded or available for Section 2.")
             # Optionally, redirect to an error page or handle differently
             return rx.redirect("/") # Fallback redirect
        
        self.select_player_b_profile() # Select the first AI profile
        return rx.redirect("/app/section2")

    @rx.event
    def proceed_to_stage_transition(self):
        """Navigate to stage transition page (between AI opponents in Section 2)."""
        self.is_stage_transition = True # Flag to show the transition UI
        # State for the next stage (e.g. opponent balance) is reset when start_next_stage is called
        return rx.redirect("/app/stage-transition")

    @rx.var
    def stage_total_invested(self) -> int:
        # Sum of amount_sent for the current stage
        return sum(
            r.get("amount_sent", 0)
            for r in self.round_history
            if r.get("stage")
            == self.current_stage - 1  # stage_transition is shown after stage increment
        )

    @rx.var
    def stage_total_returned(self) -> int:
        # Sum of amount_returned for the current stage
        return sum(
            r.get("amount_returned", 0)
            for r in self.round_history
            if r.get("stage") == self.current_stage - 1
        )

    @rx.var
    def stage_net_payoff(self) -> int:
        # Net payoff for player A in the stage
        return sum(
            r.get("player_a_current_round_payoff", 0)
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
            sum(
                r.get("amount_sent", 0)
                for r in self.round_history
                if r.get("stage") == i
            )
            for i in range(num_stages)
        ]

    @rx.var
    def all_stages_total_returned(self) -> list:
        # List of total returned per stage
        if not self.shuffled_profiles:
            return []
        num_stages = len(self.shuffled_profiles)
        return [
            sum(
                r.get("amount_returned", 0)
                for r in self.round_history
                if r.get("stage") == i
            )
            for i in range(num_stages)
        ]

    @rx.var
    def all_stages_net_payoff(self) -> list:
        # List of net payoff per stage
        if not self.shuffled_profiles:
            return []
        num_stages = len(self.shuffled_profiles)
        return [
            sum(
                r.get("player_a_current_round_payoff", 0)
                for r in self.round_history
                if r.get("stage") == i
            )
            for i in range(num_stages)
        ]

    @rx.var
    def all_stages_end_balance(self) -> list:
        # List of end balance per stage (cumulative)
        if not self.shuffled_profiles:
            return []
        num_stages = len(self.shuffled_profiles)
        balances = []
        running_balance = self.player_a_balance - sum(
            self.all_stages_net_payoff
        )  # back-calculate initial
        for i in range(num_stages):
            running_balance += self.all_stages_net_payoff[i]
            balances.append(running_balance)
        return balances

    @rx.event_handler("auth.logout_event")
    def handle_logout_event(self):
        """Handles the logout event emitted by AuthState."""
        print("[TrustGameState] Received logout event. Resetting game state.")
        self.reset_game_state() # Call existing reset method

    @rx.event_handler("auth.set_user_identity")
    def handle_set_user_identity(self, payload: dict):
        """Handles the set_user_identity event emitted by AuthState."""
        user_id = payload.get("user_id")
        user_email = payload.get("user_email")
        if user_id is not None and user_email is not None:
            print(f"[TrustGameState] Received set_user_identity event. User ID: {user_id}, Email: {user_email}")
            self.set_user_identity(user_id, user_email) # Call existing method
        else:
            print("[TrustGameState] Error: Received set_user_identity event with missing user_id or user_email.")
