import random
from typing import List
import reflex as rx
from .firebase_db import save_experiment_data
# from Trust_Web.trust_game_state import TrustGameState
# from Trust_Web.authentication import AuthState
# from reflex.utils import get_value


INITIAL_ENDOWMENT = 100
MULTIPLIER = 1.5
NUM_COMPUTER_PLAYERS = 4
TOTAL_ROUNDS = 3


class PublicGoodState(rx.State):
    """
    State for the Public Goods Game.
    Handles user input, simulates computer players, and computes payoffs.
    """

    # User input
    human_contribution: int = 0
    contribution_error: str = ""
    user_id: str = ""
    user_email: str = ""

    # Game state
    current_round: int = 0
    human_balance: int = INITIAL_ENDOWMENT
    computer_balances: List[int] = [INITIAL_ENDOWMENT] * NUM_COMPUTER_PLAYERS
    computer_contributions: List[int] = []
    total_contribution: int = 0  # 사람과 컴퓨터의 기여금 합
    multiplied_pool: float = 0.0  # 기여금 합에 MULTIPLIER을 곱한 총 사업이득
    per_share: float = 0.0  # 각 플레이어가 받을 배당액
    human_payoff: float = 0.0  # 사람의 최종 이익
    computer_payoffs: List[float] = [0.0] * NUM_COMPUTER_PLAYERS  # Correctly initialized
    game_played: bool = False
    game_finished: bool = False
    game_began_at: str = ""

    @rx.event
    def set_human_contribution(self, value: str) -> None:
        """Set the human player's contribution, with validation."""
        try:
            c = int(value)
            if c < 0 or c > (self.human_balance // 2):
                self.contribution_error = f"Contribution must be between 0 and {self.human_balance // 2}."
                self.human_contribution = 0  # 잘못된 입력 시 값을 0으로 리셋
            else:
                self.human_contribution = c
                self.contribution_error = ""
        except ValueError:
            self.contribution_error = "Please enter a valid integer."
            self.human_contribution = 0  # 잘못된 입력 시 값을 0으로 리셋

    @rx.event
    def play_game(self) -> None:
        """
        Simulate the Public Goods Game round.
        - Accepts human contribution.
        - Simulates computer contributions.
        - Calculates total, multiplied pool, per-share, and payoffs.
        """
        # # Validate inputs
        # if self.human_contribution < 0 or self.human_contribution > self.human_balance:
        #     self.contribution_error = f"투자 가능한 금액은 0에서 {self.human_balance // 2} 사이입니다."
        #     return

        # Total number of players is the number of computer players + 1 human player
        total_players = NUM_COMPUTER_PLAYERS + 1

        # Simulate computer contributions (based on their current balance)
        # 컴퓨터는 현재 잔액의 절반 이하를 기여할 수 있다.
        self.computer_contributions = [
            random.randint(0, balance // 2) if balance > 0 else 0 for balance in self.computer_balances
        ]

        # Calculate total contribution
        self.total_contribution = self.human_contribution + sum(self.computer_contributions)

        # Multiply the pool
        self.multiplied_pool = self.total_contribution * MULTIPLIER

        # Calculate per-participant share
        if total_players > 0:
            self.per_share = self.multiplied_pool / total_players
        else:
            self.per_share = 0.0

        # Calculate payoffs and update balances
        current_round_human_payoff = self.per_share - self.human_contribution
        self.human_payoff = current_round_human_payoff  # Store this round's payoff for display
        self.human_balance += int(current_round_human_payoff)

        for i, (contribution, balance) in enumerate(zip(self.computer_contributions, self.computer_balances)):
            current_round_computer_payoff = self.per_share - contribution
            self.computer_payoffs[i] = current_round_computer_payoff  # Store this round's payoff for display
            self.computer_balances[i] += int(current_round_computer_payoff)

        self.game_played = True

        # 게임 시작 시점 기록
        if not self.game_began_at:
            import datetime
            self.game_began_at = datetime.datetime.now().isoformat()

        print(f"type of get_value: {type(self.get_value('user_id'))}")
        print(f"type of get_value: {type(self.get_value('user_email'))}")
        print(f"type of get_value: {type(self.get_value('game_began_at'))}")
        print(f"type of get_value: {type(self.get_value('current_round'))}")
        print(f"type of get_value: {type(self.get_value('human_contribution'))}")
        print(f"type of get_value: {type(self.get_value('computer_contributions'))}")
        print(f"type of get_value: {type(self.get_value('human_payoff'))}")

        # user_id = str(AuthState.user_id)
        # user_email = str(AuthState.user_email)
        transaction = {
            "user_id": self.user_id,
            "user_email": self.user_email,
            "game_name": "public_goods_game",
            "game_began_at": self.get_value("game_began_at"),
            "round": self.get_value("current_round") + 1,  # display_round_number와 맞추기 위해 +1
            "human_contribution": self.get_value("human_contribution"),
            "computer_contributions": [self.get_value(c) for c in self.computer_contributions],
            "human_payoff": self.get_value("human_payoff"),
        }
        save_experiment_data(self.user_id, transaction)

    @rx.event
    def prepare_next_round(self) -> None:
        """Prepare the state for the next round."""
        self.current_round += 1
        self.game_played = False
        self.human_contribution = 0
        self.contribution_error = ""
        if self.current_round >= TOTAL_ROUNDS:
            self.game_finished = True
        # Results like total_contribution, multiplied_pool, per_share, human_payoff, computer_contributions, computer_payoffs
        # will be recalculated and overwritten in the next play_game call.

    @rx.event
    def reset_game(self) -> None:
        """Reset the game state for a new game."""
        self.human_contribution = 0
        self.computer_contributions = []
        self.total_contribution = 0
        self.multiplied_pool = 0.0
        self.per_share = 0.0
        self.human_payoff = 0.0
        self.computer_payoffs = [0.0] * NUM_COMPUTER_PLAYERS  # Reset payoffs
        self.game_played = False
        self.contribution_error = ""
        self.current_round = 0
        self.human_balance = INITIAL_ENDOWMENT
        self.computer_balances = [INITIAL_ENDOWMENT] * NUM_COMPUTER_PLAYERS
        self.game_finished = False

    @rx.event
    def set_user_identity(self, user_id: str, user_email: str):
        """Sets the user ID and email for the public goods state."""
        print(f"[DEBUG] Setting user identity in PublicGoodState: {user_id}, {user_email}")
        self.user_id = user_id
        self.user_email = user_email

    @rx.var
    def computer_contributions_str(self) -> str:
        """Return a readable string of computer contributions."""
        if not self.computer_contributions:
            return "Computers have not contributed yet in this round."
        return ", ".join(f"{c}" for c in self.computer_contributions)

    @rx.var
    def display_round_number(self) -> int:
        """Returns the 1-indexed current round number for display."""
        if self.game_finished and self.current_round == TOTAL_ROUNDS:
            return TOTAL_ROUNDS
        return self.current_round + 1

    @rx.var
    def multiplied_pool_str(self) -> str:
        """Return the multiplied pool formatted to 0 decimal places."""
        return f"{self.multiplied_pool:.0f}"

    @rx.var
    def per_share_str(self) -> str:
        """Return the per share amount formatted to 0 decimal places."""
        return f"{self.per_share:.0f}"

    @rx.var
    def human_payoff_str(self) -> str:
        """Return the human payoff formatted to 0 decimal places."""
        return f"{self.human_payoff:.0f}"
