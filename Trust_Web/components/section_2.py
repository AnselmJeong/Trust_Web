import reflex as rx
from Trust_Web.state import GameState, NUM_ROUNDS
from .common_styles import COLORS, STYLES
from .stage_transition import stage_transition


def section_2() -> rx.Component:
    """Section 2 component styled similarly to section_1()."""
    balance = GameState.player_a_balance
    max_send = GameState.max_send_amount
    round_str = GameState.round_str
    # Define the main vstack content first for clarity
    section_content = rx.vstack(
        # Header: Section title and round info
        rx.hstack(
            rx.heading("\U0001f4c8 Section 2: You are Player A", size="6", style={"fontWeight": 600}),
            rx.spacer(),
            rx.text(round_str, color=COLORS["text_light"], size="4", style={"fontWeight": 500}),
            align="center",
            width="100%",
        ),
        # Progress bar
        rx.progress(
            value=GameState.current_round,
            max=NUM_ROUNDS,
            style={"width": "100%", "marginTop": "-8px", "marginBottom": "8px"},
        ),
        # Subtext
        rx.text(
            "Decide how much of your current balance to send to Player B.",
            color=COLORS["text_light"],
            size="4",
            style={"marginBottom": "8px"},
        ),
        # Balance/Max Send cards
        rx.hstack(
            rx.box(
                rx.text("Your Balance", color=COLORS["text_light"], size="3"),
                rx.heading(balance, size="6", style={"color": "#374151"}),
                style={
                    "background": "#f9fafb",
                    "borderRadius": "8px",
                    "padding": "16px 32px",
                    "boxShadow": "0 1px 2px rgba(0,0,0,0.03)",
                    "minWidth": "120px",
                    "textAlign": "center",
                    "flex": "1",
                },
            ),
            rx.box(
                rx.text("Max You Can Send", color=COLORS["text_light"], size="3"),
                rx.heading(max_send, size="6", style={"color": "#ef4444"}),  # Red color for limit
                style={
                    "background": "#f3f4f6",
                    "borderRadius": "8px",
                    "padding": "16px 32px",
                    "boxShadow": "0 1px 2px rgba(0,0,0,0.03)",
                    "minWidth": "120px",
                    "textAlign": "center",
                    "flex": "1",
                },
            ),
            spacing="4",
            width="100%",
            justify="center",  # Center the cards if needed
        ),
        # How much to send
        rx.text(
            "How much will you send to Player B?",
            size="5",
            style={"marginTop": "24px", "fontWeight": 500},
        ),
        rx.input(
            placeholder=f"Enter amount (0 - {max_send})",
            on_change=GameState.set_amount_to_send,
            type="number",
            id="amount_input_s2",
            style={
                "width": "100%",
                "padding": "12px",
                "fontSize": "18px",
                "borderRadius": "6px",
                "border": "1px solid #e5e7eb",
                "marginBottom": "8px",
                "minHeight": "40px",
            },
        ),
        rx.button(
            "\u2714 Submit Decision",
            on_click=[
                GameState.main_algorithm,
                rx.set_value("amount_input_s2", ""),
            ],
            style=STYLES["button"],
        ),
        # Player B's Response (conditional display might be good)
        rx.box(
            rx.cond(
                GameState.amount_to_return > -1,
                rx.vstack(
                    rx.divider(my="4"),
                    rx.text(
                        f"\U0001f4e9 Message from Player B: {GameState.message_b}",
                        size="3",
                        color=COLORS["text_light"],
                    ),
                    rx.text(
                        f"\U0001f4b0 Amount returned from Player B: {GameState.amount_to_return}",
                        size="4",
                        color="#2563eb",
                        weight="medium",
                    ),
                    spacing="2",
                    align_items="start",
                    width="100%",
                    padding_top="4",
                ),
            )
        ),
        # Profits summary
        rx.hstack(
            rx.text(
                f"\U0001f4b5 Your Balance: {GameState.player_a_balance}",
                color="#22c55e",
                size="4",
                style={"fontWeight": 500},
            ),
            rx.spacer(),
            rx.text(
                f"\U0001f464 Player B's Balance: {GameState.player_b_balance}",
                color="#3b82f6",
                size="4",
                style={"fontWeight": 500},
            ),
            style={"width": "100%", "marginTop": "12px"},
        ),
        spacing="2",
        width="100%",
        padding="20px",
    )

    return rx.cond(
        GameState.is_stage_transition,
        stage_transition(),
        # Use the same centered card structure as section_1
        rx.center(
            rx.box(
                section_content,
                style={
                    "background": "white",
                    "borderRadius": "12px",
                    "boxShadow": "0 2px 8px 0 rgba(0,0,0,0.07)",
                    "padding": "16px 32px",
                    "maxWidth": "600px",
                    "width": "100%",
                    "marginTop": "40px",
                },
            ),
            style={"minHeight": "100vh"},
        ),
    )
