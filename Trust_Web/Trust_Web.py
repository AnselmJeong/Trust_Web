import reflex as rx
from Trust_Web.state import GameState, NUM_ROUNDS


# Common Styles
COLORS = {
    "primary": "#f97316",
    "primary_dark": "#f85a05",
    "background": "#f3f4f6",
    "text": "#4b5563",
    "text_light": "#6b7280",
    "border": "#e5e7eb",
    "white": "white",
}

STYLES = {
    "page_container": {
        "width": "100%",
        "min_height": "100vh",
        "bg": COLORS["background"],
        "pt": "16",
    },
    "card": {
        "bg": COLORS["white"],
        "border_radius": "xl",
        "width": "100%",
        "max_width": "600px",
        "box_shadow": "0 1px 3px 0 rgb(0 0 0 / 0.1)",
        "padding": "8",
    },
    "heading": {
        "font_weight": 600,
        "size": "6",
        "mb": "6",
    },
    "button": {
        "bg": COLORS["primary"],
        "color": COLORS["white"],
        "font_weight": 600,
        "font_size": "18px",
        "padding": "14px 32px",
        "border_radius": "md",
        "width": "100%",
        "_hover": {"bg": COLORS["primary_dark"]},
    },
    "input": {
        "bg": COLORS["white"],
        "border": f"1px solid {COLORS['border']}",
        "p": "2",
        "border_radius": "md",
        "mb": "4",
    },
}


def page_container(*children, **kwargs) -> rx.Component:
    """Common container for all pages."""
    return rx.box(
        rx.center(
            rx.box(
                rx.vstack(
                    *children,
                    spacing="4",
                    width="100%",
                ),
                **STYLES["card"],
            ),
        ),
        **STYLES["page_container"],
        **kwargs,
    )


def primary_button(text: str, **kwargs) -> rx.Component:
    """Primary button with consistent styling."""
    return rx.button(text, **STYLES["button"], **kwargs)


def section_heading(text: str, **kwargs) -> rx.Component:
    """Section heading with consistent styling."""
    return rx.heading(text, **STYLES["heading"], **kwargs)


def login_form() -> rx.Component:
    """Login form component."""
    return rx.box(
        rx.vstack(
            # Header tabs
            rx.hstack(
                rx.box(
                    "Login",
                    bg="white",
                    p="4",
                    flex="1",
                    text_align="center",
                    border_bottom="2px solid #f97316",
                ),
                rx.box(
                    "Register",
                    bg="#f8f9fa",
                    p="4",
                    flex="1",
                    text_align="center",
                    color="#6b7280",
                ),
                spacing="0",
                width="100%",
            ),
            # Login form
            rx.vstack(
                rx.heading("Login", size="6", mb="6"),
                rx.text("Email", color="#4b5563", font_size="sm", mb="2"),
                rx.input(
                    placeholder="you@example.com",
                    on_change=GameState.set_user_email,
                    type_="email",
                    bg="white",
                    border="1px solid #e5e7eb",
                    p="2",
                    border_radius="md",
                    mb="4",
                ),
                rx.text("Password", color="#4b5563", font_size="sm", mb="2"),
                rx.input(
                    placeholder="••••••••",
                    on_change=GameState.set_password,
                    type_="password",
                    bg="white",
                    border="1px solid #e5e7eb",
                    p="2",
                    border_radius="md",
                    mb="4",
                ),
                rx.button(
                    "Login",
                    on_click=GameState.login,
                    bg="#f97316",
                    color="white",
                    width="100%",
                    p="3",
                    border_radius="md",
                    _hover={"bg": "#f85a05"},
                ),
                rx.text(GameState.auth_error, color="red", font_size="sm", mt="2"),
                rx.divider(
                    label="OR CONTINUE WITH",
                    padding_top="6",
                    padding_bottom="6",
                ),
                rx.button(
                    rx.hstack(
                        rx.image(
                            src="https://www.svgrepo.com/show/475656/google-color.svg",
                            width="5",
                            height="5",
                        ),
                        rx.text("Google"),
                        spacing="3",
                    ),
                    bg="white",
                    border="1px solid #e5e7eb",
                    width="100%",
                    p="3",
                    border_radius="md",
                    color="black",
                ),
                spacing="0",
                padding="8",
            ),
            bg="white",
            border_radius="xl",
            width="100%",
            max_width="400px",
            box_shadow="0 1px 3px 0 rgb(0 0 0 / 0.1)",
        ),
        rx.text(
            "TrustWeb Experiment Platform",
            font_size="sm",
            color="#6b7280",
            text_align="center",
            mt="8",
        ),
        width="100%",
        min_height="100vh",
        bg="#f3f4f6",
        pt="16",
    )


def instructions() -> rx.Component:
    """Instructions component."""
    return page_container(
        section_heading("Trust Game Experiment Instructions"),
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
        primary_button("I'm Ready for Section 1", on_click=GameState.start_section_1),
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
                        f"\U0001f4b0 Player A's Total Profit: {GameState.player_a_profit}",
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


def stage_transition() -> rx.Component:
    """Stage transition page between stages in Section 2."""
    return page_container(
        section_heading(f"Stage {GameState.current_stage} Complete!"),
        rx.text(
            f"""
            You have completed Stage {GameState.current_stage} with {GameState.player_b_personality}.
            
            Your current balance: {GameState.player_a_balance}
            Your total profit: {GameState.player_a_profit}
            
            Get ready for the next stage!
            """,
            color=COLORS["text_light"],
            size="4",
            style={"marginTop": "16px", "marginBottom": "24px"},
        ),
        primary_button("Start Next Stage", on_click=GameState.start_next_stage),
    )


def section_2() -> rx.Component:
    """Section 2 component."""
    return rx.cond(
        GameState.is_stage_transition,
        stage_transition(),
        page_container(
            section_heading(GameState.round_str),
            rx.text(f"Your current balance: {GameState.player_a_balance}"),
            rx.text(f"Maximum amount you can send: {GameState.max_send_amount}"),
            rx.input(
                placeholder=f"Enter amount (0 - {GameState.max_send_amount})",
                on_change=GameState.set_amount_to_send,
                type_="number",
                **STYLES["input"],
            ),
            rx.text(f"Your current profit: {GameState.player_a_profit}"),
            rx.text(f"Player B's current profit: {GameState.player_b_profit}"),
            primary_button(
                "Submit Decision",
                on_click=[GameState.main_algorithm, rx.set_value("amount_input", "")],
            ),
            rx.text(f"Message from Player B: {GameState.message_b}"),
            rx.text(f"Amount returned from Player B: {GameState.amount_to_return}"),
        ),
    )


def final_page() -> rx.Component:
    """Final page component."""
    return page_container(
        section_heading("Experiment Complete!"),
        rx.text("Thank you for participating in the Trust Game Experiment!"),
        rx.text(f"Your final balance: {GameState.player_a_balance}"),
        rx.text(f"Your total profit: {GameState.player_a_profit}"),
        rx.text(f"Player B's total profit: {GameState.player_b_profit}"),
        primary_button("Logout", on_click=GameState.logout),
    )


def transition_page() -> rx.Component:
    """Transition page between Section 1 and Section 2."""
    return rx.center(
        rx.box(
            rx.vstack(
                rx.heading("Section 1 Complete!", size="6", style={"fontWeight": 600}),
                rx.text(
                    """
                    You have completed the tutorial section where you played as Player B.
                    Now, you will play as Player A in Section 2.
                    
                    In this section:
                    - You will start with 20 currency units
                    - You can send up to 50% of your current balance in each round
                    - The amount you send will be multiplied by 2
                    - Player B (AI) will decide how much to return
                    - Your profit = Amount returned - Amount sent
                    - Player B's profit = Amount received - Amount returned
                    
                    The experiment consists of 7 rounds.
                    """,
                    color="#6b7280",
                    size="4",
                    style={"marginTop": "16px", "marginBottom": "24px"},
                ),
                rx.button(
                    "I'm Ready for Section 2",
                    on_click=GameState.start_section_2,
                    style={
                        "background": "#f97316",
                        "color": "white",
                        "fontWeight": 600,
                        "fontSize": "18px",
                        "padding": "14px 32px",
                        "borderRadius": "6px",
                    },
                ),
                spacing="4",
                width="100%",
            ),
            style={
                "background": "white",
                "borderRadius": "12px",
                "boxShadow": "0 2px 8px 0 rgba(0,0,0,0.07)",
                "padding": "32px",
                "maxWidth": "600px",
                "width": "100%",
                "marginTop": "40px",
            },
        ),
        style={"height": "100vh"},
    )


def index() -> rx.Component:
    """Main page component."""
    return rx.cond(
        GameState.is_authenticated,
        rx.cond(
            GameState.current_page == 0,
            instructions(),
            rx.cond(
                GameState.current_page == 1,
                section_1(),
                rx.cond(
                    GameState.current_page == 2,
                    transition_page(),
                    rx.cond(
                        GameState.current_page == 3,
                        section_2(),
                        final_page(),
                    ),
                ),
            ),
        ),
        login_form(),
    )


# Create the app
app = rx.App()
app.add_page(index)
