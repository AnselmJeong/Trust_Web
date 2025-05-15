import reflex as rx
from Trust_Web.trust_game_state import TrustGameState
from .common_styles import COLORS, page_container, section_heading, primary_button


def stage_transition() -> rx.Component:
    """Stage transition page styled similarly to instructions()."""
    return page_container(
        section_heading(f"Stage {TrustGameState.current_stage} Complete!"),
        rx.text(
            f"You have completed Stage {TrustGameState.current_stage} with Player B ({TrustGameState.player_b_personality}).",
            size="3",
            color=COLORS["text"],
            mb="2",
        ),
        rx.vstack(
            rx.text(
                f"\U0001f4b0 Your current balance: {TrustGameState.player_a_balance}",
                size="3",
                color=COLORS["text_light"],
            ),
            rx.text(
                f"\U0001f4b5 Your total profit so far: {TrustGameState.player_a_profit}",
                size="3",
                color=COLORS["text_light"],
            ),
            align_items="start",
            spacing="1",
            bg=COLORS["background"],
            padding="4",
            border_radius="md",
            width="100%",
            mb="4",
            border=f"1px solid {COLORS['border']}",
        ),
        rx.text(
            "Get ready for the next stage!",
            size="3",
            color=COLORS["text"],
            mb="6",
            weight="medium",
        ),
        primary_button(
            rx.hstack(
                rx.text("Start Next Stage"),
                rx.icon(tag="arrow_right", size=18),
                spacing="2",
            ),
            on_click=TrustGameState.start_next_stage,
        ),
        # Apply consistent padding within the card
        padding="20px",
    )
