import reflex as rx
from Trust_Web.trust_game_state import TrustGameState
from .common_styles import page_container, section_heading, primary_button


def final_page() -> rx.Component:
    """Final page component."""
    return page_container(
        section_heading("Experiment Complete!"),
        rx.text("Thank you for participating in the Trust Game Experiment!"),
        rx.text(f"Your final balance: {TrustGameState.player_a_balance}"),
        rx.text(f"Your total profit: {TrustGameState.player_a_profit}"),
        rx.text(f"Player B's total profit: {TrustGameState.player_b_profit}"),
        primary_button("Logout", on_click=TrustGameState.logout),
    )
