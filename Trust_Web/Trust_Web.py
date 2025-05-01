import reflex as rx
from Trust_Web.state import GameState, NUM_ROUNDS, PROLIFERATION_FACTOR


# Components
def login_form() -> rx.Component:
    """Login form component."""
    return rx.vstack(
        rx.heading("Login", size="8"),
        rx.input(
            placeholder="Email",
            on_change=GameState.set_user_email,
            type_="email",
        ),
        rx.input(
            placeholder="Password",
            on_change=GameState.set_password,
            type_="password",
        ),
        rx.button("Login", on_click=GameState.login),
        rx.button("Register", on_click=GameState.register),
        rx.text(GameState.auth_error, color="red"),
        spacing="4",
        width="100%",
        max_width="400px",
        padding="4",
    )


def instructions() -> rx.Component:
    """Instructions component."""
    return rx.vstack(
        rx.heading("Trust Game Experiment Instructions", size="8"),
        rx.text("""
        Welcome to the Trust Game Experiment! This experiment consists of two sections:

        Section 1: You will play as Player B
        - You will receive an amount from Player A
        - The amount will be multiplied by 2
        - You must decide how much to return to Player A
        - Your profit = Amount received - Amount returned
        - Player A's profit = Amount returned - Amount sent

        Section 2: You will play as Player A
        - You start with 20 currency units
        - In each round, you can send up to 50% of your current balance
        - The amount you send will be multiplied by 2
        - Player B (AI) will decide how much to return
        - Your profit = Amount returned - Amount sent
        - Player B's profit = Amount received - Amount returned

        The experiment consists of 7 rounds in each section.
        """),
        rx.button("I'm Ready", on_click=GameState.mark_ready),
        spacing="4",
        width="100%",
        max_width="800px",
        padding="4",
    )


def section_1() -> rx.Component:
    """Section 1 component styled as in the attached image."""
    sent = GameState.sent_by_a
    received = GameState.received_amount
    round_str = GameState.round_str
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
                    value=GameState.current_round,
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
                        },
                    ),
                    spacing="4",
                ),
                # How much to return
                rx.text(
                    "How much will you return to Player A?",
                    size="5",
                    style={"marginTop": "24px", "fontWeight": 500},
                ),
                rx.input(
                    placeholder=f"Enter amount (0 - {received})",
                    on_change=GameState.set_amount_to_return,
                    type_="number",
                    style={
                        "width": "100%",
                        "padding": "12px",
                        "fontSize": "18px",
                        "borderRadius": "6px",
                        "border": "1px solid #e5e7eb",
                        "marginBottom": "8px",
                    },
                ),
                rx.button(
                    "\u2714 Submit Decision",
                    on_click=GameState.submit_player_b_decision,
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
                        f"\U0001f4b5 Your Total Profit: {GameState.player_b_profit}",
                        color="#22c55e",
                        size="4",
                        style={"fontWeight": 500},
                    ),
                    rx.spacer(),
                    rx.text(
                        f"\U0001f4b0 Player A's Total Profit: {GameState.player_a_profit_section1}",
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
                "maxWidth": "420px",
                "width": "100%",
                "marginTop": "40px",
            },
        ),
        style={"height": "100vh"},
    )


def section_2() -> rx.Component:
    """Section 2 component styled to avoid direct Var arithmetic."""
    round_str = GameState.round_str
    max_send = GameState.max_send_amount
    return rx.vstack(
        rx.heading(round_str, size="7"),
        rx.text(f"Your current balance: {GameState.player_a_balance}"),
        rx.text(f"Maximum amount you can send: {max_send}"),
        rx.input(
            placeholder=f"Enter amount (0 - {max_send})",
            on_change=GameState.set_amount_to_send,
            type_="number",
        ),
        rx.text(f"Your current profit: {GameState.player_a_profit_section2}"),
        rx.text(f"Player B's current profit: {GameState.player_b_profit_section2}"),
        rx.button(
            "Submit Decision",
            on_click=[
                GameState.submit_player_a_decision,
                rx.set_value("amount_input", ""),
            ],
        ),
        rx.text(f"Message from Player B: {GameState.message_b}"),
        rx.text(f"Amount returned from Player B: {GameState.amount_returned}"),
        spacing="4",
        width="100%",
        max_width="400px",
        padding="4",
    )


def final_page() -> rx.Component:
    """Final page component."""
    return rx.vstack(
        rx.heading("Experiment Complete!", size="7"),
        rx.text("Thank you for participating in the Trust Game Experiment!"),
        rx.text(f"Your final balance: {GameState.player_a_balance}"),
        rx.text(f"Your total profit in Section 2: {GameState.player_a_profit_section2}"),
        rx.text(f"Player B's total profit in Section 2: {GameState.player_b_profit_section2}"),
        rx.button("Logout", on_click=GameState.logout),
        spacing="4",
        width="100%",
        max_width="400px",
        padding="4",
    )


def index() -> rx.Component:
    """Main page component."""
    return rx.cond(
        GameState.is_authenticated,
        rx.cond(
            GameState.current_section == 0,
            instructions(),
            rx.cond(
                GameState.current_section == 1,
                section_1(),
                rx.cond(GameState.current_section == 2, section_2(), final_page()),
            ),
        ),
        login_form(),
    )


# Create the app
app = rx.App()
app.add_page(index)
