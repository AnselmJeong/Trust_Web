import reflex as rx
from Trust_Web.public_goods_state import (
    PublicGoodState,
    TOTAL_ROUNDS,
    NUM_COMPUTER_PLAYERS,
    MULTIPLIER,
)
from Trust_Web.trust_game_state import TrustGameState


def public_goods_game_component() -> rx.Component:
    """UI component for the Public Goods Game."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon(tag="users", mr=2),
                rx.heading("Public Goods Game", size="7"),
                rx.spacer(),
                rx.text(
                    rx.text(PublicGoodState.display_round_number, font_weight="bold"),
                    f" / {TOTAL_ROUNDS} Rounds",
                    color_scheme="gray",
                ),
                justify="between",
                align_items="center",
                width="100%",
            ),
            rx.progress(
                value=PublicGoodState.current_round,
                max_=TOTAL_ROUNDS,
                width="100%",
                color_scheme="blue",
                height="sm",
                border_radius="md",
            ),
            rx.text(
                f"Participants: {NUM_COMPUTER_PLAYERS + 1} (You and {NUM_COMPUTER_PLAYERS} computer players)",
                size="2",
                color_scheme="gray",
            ),
            rx.text(
                f"Your current balance: {PublicGoodState.human_balance}",
                size="2",
                color_scheme="gray",
            ),
            rx.text(f"Contribution Multiplier: x{MULTIPLIER}", size="2", color_scheme="gray"),
            rx.divider(),
            rx.cond(
                ~PublicGoodState.game_finished,
                rx.vstack(
                    rx.text("How much will you contribute to the common pool?"),
                    rx.input(
                        placeholder=f"Enter amount (0 - {PublicGoodState.human_balance})",
                        value=PublicGoodState.human_contribution.to_string(),
                        on_change=PublicGoodState.set_human_contribution,
                        type="number",
                        is_disabled=PublicGoodState.game_played,
                    ),
                    rx.cond(
                        PublicGoodState.contribution_error != "",
                        rx.text(PublicGoodState.contribution_error, color_scheme="red", size="2"),
                    ),
                    align_items="stretch",
                    spacing="2",
                    width="100%",
                ),
            ),
            rx.cond(
                PublicGoodState.game_finished,
                rx.button(
                    "Proceed to Trust Game",
                    on_click=TrustGameState.go_to_trust_game_instructions,
                    width="100%",
                    size="3",
                    color_scheme="green",
                ),
                rx.cond(
                    PublicGoodState.game_played,
                    rx.button(
                        "Next Round",
                        on_click=PublicGoodState.prepare_next_round,
                        width="100%",
                        size="3",
                        color_scheme="blue",
                    ),
                    rx.button(
                        "Submit Decision",
                        on_click=PublicGoodState.play_game,
                        width="100%",
                        size="3",
                        color_scheme="gray",
                        is_disabled=(PublicGoodState.contribution_error != ""),
                    ),
                ),
            ),
            rx.cond(
                PublicGoodState.game_played,
                rx.vstack(
                    rx.heading("Round Results", size="5", margin_top="4"),
                    rx.text(PublicGoodState.computer_contributions_str, white_space="pre-wrap"),
                    rx.divider(),
                    rx.hstack(
                        rx.vstack(
                            rx.text("Total Pool", size="2", color_scheme="gray"),
                            rx.heading(PublicGoodState.total_contribution.to_string(), size="8"),
                            align_items="center",
                            flex_grow=1,
                            text_align="center",
                        ),
                        rx.vstack(
                            rx.text("Multiplied Amount", size="2", color_scheme="gray"),
                            rx.heading(PublicGoodState.multiplied_pool_str, size="8"),
                            align_items="center",
                            flex_grow=1,
                            text_align="center",
                        ),
                        rx.vstack(
                            rx.text("Your Share", size="2", color_scheme="gray"),
                            rx.heading(PublicGoodState.per_share_str, size="8"),
                            align_items="center",
                            flex_grow=1,
                            text_align="center",
                        ),
                        justify="between",
                        width="100%",
                        spacing="4",
                        padding_y="2",
                    ),
                    rx.divider(),
                    rx.vstack(
                        rx.text("Your payoff this round", size="5", color_scheme="gray"),
                        rx.heading(PublicGoodState.human_payoff_str, size="9"),
                        align_items="center",
                        padding_y="2",
                    ),
                    rx.text(
                        f"Your new balance: {PublicGoodState.human_balance}",
                        size="2",
                        color_scheme="gray",
                        text_align="center",
                        width="100%",
                    ),
                    spacing="3",
                    width="100%",
                    align_items="stretch",
                    padding="4",
                    border="1px solid #ddd",
                    border_radius="md",
                    margin_top="4",
                ),
            ),
            spacing="4",
            align_items="stretch",
        ),
        width="clamp(300px, 80%, 600px)",
        margin_x="auto",
        margin_top="2em",
        padding="6",
    )
