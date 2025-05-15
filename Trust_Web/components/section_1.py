import reflex as rx
from Trust_Web.trust_game_state import TrustGameState, NUM_ROUNDS
from .common_styles import COLORS


def section_1() -> rx.Component:
    """Section 1 component styled as in the attached image."""
    sent = TrustGameState.amount_to_send
    received = TrustGameState.received_amount
    round_str = TrustGameState.round_str
    return rx.center(
        rx.box(
            rx.vstack(
                # Header: Section title and round info
                rx.hstack(
                    rx.heading(
                        "\U0001f464 Section 1: You are Player B",
                        size="6",
                        style={"fontWeight": 600},
                    ),
                    rx.spacer(),
                    rx.text(round_str, color="#6b7280", size="4", style={"fontWeight": 500}),
                    align="center",
                    width="100%",
                ),
                # Progress bar
                rx.progress(
                    value=TrustGameState.current_round,
                    max=NUM_ROUNDS,
                    style={"width": "100%", "marginTop": "-8px", "marginBottom": "8px"},
                ),
                # Subtext
                rx.text(
                    "Player A has sent you points. Decide how much to return.",
                    color="#6b7280",
                    size="4",
                    style={"marginBottom": "8px"},
                ),
                # Sent/Received cards
                rx.hstack(
                    rx.box(
                        rx.text("Player A Sent", color="#6b7280", size="3"),
                        rx.heading(sent, size="6", style={"color": "#374151"}),
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
                        rx.text("You Received", color="#6b7280", size="3"),
                        rx.heading(received, size="6", style={"color": "#2563eb"}),
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
                ),
                # How much to return
                rx.text(
                    "How much will you return to Player A?",
                    size="5",
                    style={"marginTop": "24px", "fontWeight": 500},
                ),
                rx.input(
                    placeholder=f"Enter amount (0 - {received})",
                    on_change=TrustGameState.set_amount_to_return,
                    type="number",
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
                    on_click=TrustGameState.submit_player_b_decision,
                    style={
                        "width": "100%",
                        "background": "#f97316",
                        "color": "white",
                        "fontWeight": 600,
                        "fontSize": "18px",
                        "padding": "14px 0",
                        "borderRadius": "6px",
                        "marginTop": "8px",
                        "marginBottom": "8px",
                    },
                ),
                # Profits summary
                rx.hstack(
                    rx.text(
                        f"\U0001f4b5 Your Total Profit: {TrustGameState.player_b_profit}",
                        color="#22c55e",
                        size="4",
                        style={"fontWeight": 500},
                    ),
                    rx.spacer(),
                    rx.text(
                        f"\U0001f4b0 Player A's Total Profit: {TrustGameState.player_a_profit}",
                        color="#3b82f6",
                        size="4",
                        style={"fontWeight": 500},
                    ),
                    style={"width": "100%", "marginTop": "12px"},
                ),
                spacing="2",
                width="100%",
            ),
            style={
                "background": "white",
                "borderRadius": "12px",
                "boxShadow": "0 2px 8px 0 rgba(0,0,0,0.07)",
                "padding": "32px 32px 16px 32px",
                "maxWidth": "600px",
                "width": "100%",
                "marginTop": "40px",
            },
        ),
        style={"height": "100vh"},
    )
