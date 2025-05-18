import reflex as rx
from Trust_Web.trust_game_state import TrustGameState
from ..authentication import AuthState
from .common_styles import page_container, section_heading, primary_button


def final_page() -> rx.Component:
    """Final page component."""
    return page_container(
        section_heading("Experiment Complete!"),
        rx.text("Thank you for participating in the Trust Game Experiment!"),
        rx.text(f"Your final balance: {TrustGameState.player_a_balance}"),
        rx.text(f"Your total profit: {TrustGameState.player_a_total_profit_in_section2}"),
        rx.text(f"Player B's total profit: {TrustGameState.player_b_balance}"),
        rx.text(
            "Your total profit is calculated based on the transactions you made in Section 2 of the experiment.",
            align_items="center",
            spacing="4",
        ),
        primary_button("Back to Login", on_click=AuthState.logout),
    )
