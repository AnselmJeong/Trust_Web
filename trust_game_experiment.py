import reflex as rx
from state import GameState, NUM_ROUNDS, PROLIFERATION_FACTOR, INITIAL_BALANCE


def index():
    """The main page of the application."""
    return rx.vstack(
        rx.heading("Trust Game Experiment", size="1"),
        rx.cond(
            ~GameState.is_authenticated,
            login_form(),
            rx.cond(
                GameState.current_section == 0,
                instructions(),
                rx.cond(
                    GameState.current_section == 1,
                    player_b_round(),
                    rx.cond(GameState.current_section == 2, player_a_round(), results()),
                ),
            ),
        ),
        spacing="4",
        padding="4",
    )


def login_form():
    """The login form component."""
    return rx.vstack(
        rx.heading("Login or Register", size="2"),
        rx.input(
            placeholder="Email",
            value=GameState.user_email,
            on_change=GameState.set_user_email,
            type_="email",
        ),
        rx.input(
            placeholder="Password",
            value=GameState.password,
            on_change=GameState.set_password,
            type_="password",
        ),
        rx.hstack(
            rx.button("Login", on_click=GameState.login),
            rx.button("Register", on_click=GameState.register),
        ),
        rx.cond(GameState.auth_error != "", rx.text(GameState.auth_error, color="red")),
        spacing="4",
    )


def instructions():
    """The instructions component."""
    return rx.vstack(
        rx.heading("Instructions", size="2"),
        rx.text(
            """
        In this experiment, you will play two roles in a trust game:
        
        1. First as Player B: You will receive an amount from Player A and decide how much to return.
        2. Then as Player A: You will decide how much to send to Player B.
        
        Each role will be played for {} rounds.
        """.format(NUM_ROUNDS)
        ),
        rx.button("I'm Ready", on_click=GameState.mark_ready),
        spacing="4",
    )


def player_b_round():
    """The Player B round component."""
    return rx.vstack(
        rx.heading(f"Round {GameState.current_round} - Player B", size="2"),
        rx.text(f"Player A sent you: {GameState.sent_by_a}"),
        rx.text(f"Maximum you can return: {GameState.sent_by_a * PROLIFERATION_FACTOR}"),
        rx.text(f"Your current profit: {GameState.player_b_profit}"),
        rx.text(f"Player A's current profit: {GameState.player_a_profit_section1}"),
        rx.input(
            placeholder="Amount to return",
            value=GameState.amount_to_return,
            on_change=GameState.set_amount_to_return,
        ),
        rx.button("Submit", on_click=GameState.submit_player_b_decision),
        spacing="4",
    )


def player_a_round():
    """The Player A round component."""
    return rx.vstack(
        rx.heading(f"Round {GameState.current_round} - Player A", size="2"),
        rx.text(f"Your current balance: {GameState.player_a_balance}"),
        rx.text(f"Maximum you can send: {GameState.player_a_balance // 2}"),
        rx.text(f"Your current profit: {GameState.player_a_profit_section2}"),
        rx.text(f"Player B's current profit: {GameState.player_b_profit_section2}"),
        rx.input(
            placeholder="Amount to send",
            value=GameState.amount_to_send,
            on_change=GameState.set_amount_to_send,
        ),
        rx.button("Submit", on_click=GameState.submit_player_a_decision),
        spacing="4",
    )


def results():
    """The results component."""
    return rx.vstack(
        rx.heading("Experiment Complete", size="2"),
        rx.text("Section 1 (Player B):"),
        rx.text(f"Your total profit: {GameState.player_b_profit}"),
        rx.text(f"Player A's total profit: {GameState.player_a_profit_section1}"),
        rx.text("Section 2 (Player A):"),
        rx.text(f"Your total profit: {GameState.player_a_profit_section2}"),
        rx.text(f"Player B's total profit: {GameState.player_b_profit_section2}"),
        rx.button("Logout", on_click=GameState.logout),
        spacing="4",
    )


# Create the app
app = rx.App()
app.add_page(index)
