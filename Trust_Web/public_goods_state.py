import random
from typing import List
import reflex as rx

INITIAL_ENDOWMENT = 100
MULTIPLIER = 1.5
MIN_PARTICIPANTS = 2


class PublicGoodState(rx.State):
    """
    State for the Public Goods Game.
    Handles user input, simulates computer players, and computes payoffs.
    """

    # User input
    num_participants: int = 4  # Default to 4 participants
    human_contribution: int = 0
    contribution_error: str = ""
    num_participants_error: str = ""

    # Game state
    computer_contributions: List[int] = []
    total_contribution: int = 0
    multiplied_pool: float = 0.0
    per_share: float = 0.0
    human_payoff: float = 0.0
    computer_payoffs: List[float] = []
    game_played: bool = False

    @rx.event
    def set_num_participants(self, value: str) -> None:
        """Set the number of participants, with validation."""
        try:
            n = int(value)
            if n < MIN_PARTICIPANTS:
                self.num_participants_error = (
                    f"Number of participants must be at least {MIN_PARTICIPANTS}."
                )
            else:
                self.num_participants = n
                self.num_participants_error = ""
        except ValueError:
            self.num_participants_error = "Please enter a valid integer."

    @rx.event
    def set_human_contribution(self, value: str) -> None:
        """Set the human player's contribution, with validation."""
        try:
            c = int(value)
            if c < 0 or c > INITIAL_ENDOWMENT:
                self.contribution_error = f"Contribution must be between 0 and {INITIAL_ENDOWMENT}."
            else:
                self.human_contribution = c
                self.contribution_error = ""
        except ValueError:
            self.contribution_error = "Please enter a valid integer."

    @rx.event
    def play_game(self) -> None:
        """
        Simulate the Public Goods Game round.
        - Accepts human contribution and number of participants.
        - Simulates computer contributions.
        - Calculates total, multiplied pool, per-share, and payoffs.
        """
        # Validate inputs
        if self.num_participants < MIN_PARTICIPANTS:
            self.num_participants_error = (
                f"Number of participants must be at least {MIN_PARTICIPANTS}."
            )
            return
        if self.human_contribution < 0 or self.human_contribution > INITIAL_ENDOWMENT:
            self.contribution_error = f"Contribution must be between 0 and {INITIAL_ENDOWMENT}."
            return

        # Simulate computer contributions
        self.computer_contributions = [
            random.randint(0, INITIAL_ENDOWMENT) for _ in range(self.num_participants - 1)
        ]

        # Calculate total contribution
        self.total_contribution = self.human_contribution + sum(self.computer_contributions)

        # Multiply the pool
        self.multiplied_pool = self.total_contribution * MULTIPLIER

        # Calculate per-participant share
        self.per_share = self.multiplied_pool / self.num_participants

        # Calculate payoffs
        self.human_payoff = (INITIAL_ENDOWMENT - self.human_contribution) + self.per_share
        self.computer_payoffs = [
            (INITIAL_ENDOWMENT - c) + self.per_share for c in self.computer_contributions
        ]
        self.game_played = True

    @rx.event
    def reset_game(self) -> None:
        """Reset the game state for a new round."""
        self.human_contribution = 0
        self.computer_contributions = []
        self.total_contribution = 0
        self.multiplied_pool = 0.0
        self.per_share = 0.0
        self.human_payoff = 0.0
        self.computer_payoffs = []
        self.game_played = False
        self.contribution_error = ""
        self.num_participants_error = ""

    @rx.var
    def computer_contributions_str(self) -> str:
        """Return a readable string of computer contributions."""
        return ", ".join(
            f"Computer {i + 1}: {c}" for i, c in enumerate(self.computer_contributions)
        )
