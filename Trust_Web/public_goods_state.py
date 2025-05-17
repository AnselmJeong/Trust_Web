import random
from typing import List
import reflex as rx

INITIAL_ENDOWMENT = 100
MULTIPLIER = 1.5
NUM_COMPUTER_PLAYERS = 4
TOTAL_ROUNDS = 10


class PublicGoodState(rx.State):
    """
    State for the Public Goods Game.
    Handles user input, simulates computer players, and computes payoffs.
    """

    # User input
    human_contribution: int = 0
    contribution_error: str = ""

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

    @rx.event
    def set_human_contribution(self, value: str) -> None:
        """Set the human player's contribution, with validation."""
        try:
            c = int(value)
            if c < 0 or c > self.human_balance:
                self.contribution_error = (
                    f"Contribution must be between 0 and {self.human_balance}."
                )
            else:
                self.human_contribution = c
                self.contribution_error = ""
        except ValueError:
            self.contribution_error = "Please enter a valid integer."

    @rx.event
    def play_game(self) -> None:
        """
        Simulate the Public Goods Game round.
        - Accepts human contribution.
        - Simulates computer contributions.
        - Calculates total, multiplied pool, per-share, and payoffs.
        """
        # Validate inputs
        if self.human_contribution < 0 or self.human_contribution > self.human_balance:
            self.contribution_error = f"Contribution must be between 0 and {self.human_balance}."
            return

        # Total number of players is the number of computer players + 1 human player
        total_players = NUM_COMPUTER_PLAYERS + 1

        # Simulate computer contributions (based on their current balance)
        # 컴퓨터는 현재 잔액의 절반 이하를 기여할 수 있다.
        self.computer_contributions = [
            random.randint(0, balance // 2) if balance > 0 else 0
            for balance in self.computer_balances
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

        for i, (contribution, balance) in enumerate(
            zip(self.computer_contributions, self.computer_balances)
        ):
            current_round_computer_payoff = self.per_share - contribution
            self.computer_payoffs[i] = (
                current_round_computer_payoff  # Store this round's payoff for display
            )
            self.computer_balances[i] += int(current_round_computer_payoff)

        self.game_played = True
        self.current_round += 1

        # Check if game is finished
        if self.current_round >= TOTAL_ROUNDS:
            self.game_finished = True

    @rx.event
    def prepare_next_round(self) -> None:
        """Prepare the state for the next round."""
        self.game_played = False
        self.human_contribution = 0
        self.contribution_error = ""
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

    @rx.var
    def computer_contributions_str(self) -> str:
        """Return a readable string of computer contributions."""
        if not self.computer_contributions:
            return "Computers have not contributed yet in this round."
        return ", ".join(
            f"Computer {i + 1} contributed {c}" for i, c in enumerate(self.computer_contributions)
        )

    @rx.var
    def display_round_number(self) -> int:
        """Returns the 1-indexed current round number for display."""
        if self.game_finished and self.current_round == TOTAL_ROUNDS:
            return TOTAL_ROUNDS
        return self.current_round + 1
