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
    container_style = STYLES["page_container"].copy()
    card_style = STYLES["card"].copy()

    padding_top = kwargs.pop("padding_top", container_style.pop("pt", "16"))
    padding_x = kwargs.pop("padding_x", None)

    container_style["pt"] = padding_top
    if padding_x:
        container_style["px"] = padding_x

    return rx.box(
        rx.center(
            rx.box(
                *children,
                **card_style,
            ),
        ),
        **container_style,
        **kwargs,
    )


def primary_button(text: str, **kwargs) -> rx.Component:
    """Primary button with consistent styling."""
    return rx.button(text, **STYLES["button"], **kwargs)


def section_heading(text: str, **kwargs) -> rx.Component:
    """Section heading with consistent styling."""
    return rx.heading(text, **STYLES["heading"], **kwargs)


def login_form() -> rx.Component:
    """Login form component using rx.tabs for Login/Register."""
    return rx.box(
        # Top bar branding
        rx.box(
            rx.text("TrustWeb", color="#0ea5e9", font_weight="bold", font_size="xl"),
            bg="#f3f4f6",
            width="100%",
            p="4",
            border_bottom="1px solid #e5e7eb",
        ),
        # Centered content area
        rx.center(
            rx.box(
                # Using rx.tabs for the Login/Register section
                rx.tabs.root(
                    rx.tabs.list(
                        rx.tabs.trigger("Login", value="login"),
                        rx.tabs.trigger("Register", value="register"),
                        width="100%",
                        justify="center",
                        border_bottom="1px solid #e5e7eb",
                    ),
                    # Login Tab Content
                    rx.tabs.content(
                        rx.vstack(
                            rx.heading("Login", size="5", mb="4", mt="6"),
                            # Email Field
                            rx.text(
                                "Email",
                                color="#4b5563",
                                font_size="sm",
                                mb="1",
                                align_self="flex-start",
                            ),
                            rx.input(
                                placeholder="you@example.com",
                                on_change=GameState.set_user_email,
                                type_="email",
                                bg="white",
                                border="1px solid #e5e7eb",
                                p="2",
                                border_radius="md",
                                mb="3",
                                width="100%",
                            ),
                            # Password Field
                            rx.text(
                                "Password",
                                color="#4b5563",
                                font_size="sm",
                                mb="1",
                                align_self="flex-start",
                            ),
                            rx.input(
                                placeholder="••••••••",
                                on_change=GameState.set_password,
                                type_="password",
                                bg="white",
                                border="1px solid #e5e7eb",
                                p="2",
                                border_radius="md",
                                mb="4",
                                width="100%",
                            ),
                            # Spacer to align Login button with Register button
                            rx.box(height="68px"),
                            # Login Button
                            rx.button(
                                "Login",
                                on_click=GameState.login,
                                bg="#f97316",  # Orange color from image
                                color="white",
                                width="100%",
                                p="3",
                                border_radius="md",
                                font_weight="bold",
                                font_size="md",
                                mb="4",
                                _hover={"bg": "#f85a05"},
                            ),
                            rx.text(
                                GameState.auth_error, color="red", font_size="sm", mt="-2", mb="2"
                            ),
                            rx.hstack(
                                rx.divider(border_color="#e5e7eb"),
                                rx.text(
                                    "OR CONTINUE WITH",
                                    color="#6b7280",
                                    font_size="xs",
                                    white_space="nowrap",
                                    px="2",
                                ),
                                rx.divider(border_color="#e5e7eb"),
                                width="100%",
                                align_items="center",
                                my="2",
                            ),
                            rx.button(
                                rx.hstack(
                                    rx.image(
                                        src="/google-icon.svg",
                                        width="1.25em",
                                        height="1.25em",
                                    ),
                                    rx.text("Google"),
                                    spacing="2",
                                    align_items="center",
                                ),
                                bg="white",
                                border="1px solid #e5e7eb",
                                width="100%",
                                p="3",
                                border_radius="md",
                                color="black",
                                font_weight="medium",
                            ),
                            spacing="3",
                            width="100%",
                            padding="20px",
                            align_items="stretch",
                            min_height="450px",
                        ),
                        value="login",
                        pt="4",
                    ),
                    # Register Tab Content
                    rx.tabs.content(
                        rx.vstack(
                            rx.heading("Register", size="5", mb="4", mt="6"),
                            # Email Field
                            rx.text(
                                "Email",
                                color="#4b5563",
                                font_size="sm",
                                mb="1",
                                align_self="flex-start",
                            ),
                            rx.input(
                                placeholder="you@example.com",
                                on_change=GameState.set_user_email,
                                type_="email",
                                bg="white",
                                border="1px solid #e5e7eb",
                                p="2",
                                border_radius="md",
                                mb="3",
                                width="100%",
                            ),
                            # Password Field
                            rx.text(
                                "Password",
                                color="#4b5563",
                                font_size="sm",
                                mb="1",
                                align_self="flex-start",
                            ),
                            rx.input(
                                placeholder="••••••••",
                                on_change=GameState.set_password,
                                type_="password",
                                bg="white",
                                border="1px solid #e5e7eb",
                                p="2",
                                border_radius="md",
                                mb="3",
                                width="100%",
                            ),
                            # Confirm Password Field
                            rx.text(
                                "Confirm Password",
                                color="#4b5563",
                                font_size="sm",
                                mb="1",
                                align_self="flex-start",
                            ),
                            rx.input(
                                placeholder="••••••••",
                                on_change=GameState.set_confirm_password,
                                type_="password",
                                bg="white",
                                border="1px solid #e5e7eb",
                                p="2",
                                border_radius="md",
                                mb="4",
                                width="100%",
                            ),
                            # Register Button
                            rx.button(
                                "Register",
                                on_click=GameState.register,
                                bg="#f97316",
                                color="white",
                                width="100%",
                                p="3",
                                border_radius="md",
                                font_weight="bold",
                                font_size="md",
                                mb="4",
                                _hover={"bg": "#f85a05"},
                            ),
                            rx.text(
                                GameState.auth_error, color="red", font_size="sm", mt="-2", mb="2"
                            ),
                            # Divider and Google Button (same as login)
                            rx.hstack(
                                rx.divider(border_color="#e5e7eb"),
                                rx.text(
                                    "OR CONTINUE WITH",
                                    color="#6b7280",
                                    font_size="xs",
                                    white_space="nowrap",
                                    px="2",
                                ),
                                rx.divider(border_color="#e5e7eb"),
                                width="100%",
                                align_items="center",
                                my="2",
                            ),
                            rx.button(
                                rx.hstack(
                                    rx.image(
                                        src="/google-icon.svg",
                                        width="1.25em",
                                        height="1.25em",
                                    ),
                                    rx.text("Google"),
                                    spacing="2",
                                    align_items="center",
                                ),
                                bg="white",
                                border="1px solid #e5e7eb",
                                width="100%",
                                p="3",
                                border_radius="md",
                                color="black",
                                font_weight="medium",
                            ),
                            spacing="3",
                            width="100%",
                            padding="20px",
                            align_items="stretch",
                            min_height="450px",
                        ),
                        value="register",
                        pt="4",
                    ),
                    default_value="login",  # Start with the Login tab selected
                    width="100%",
                    bg="white",
                    border_radius="md",
                    box_shadow="0 1px 3px 0 rgb(0 0 0 / 0.1)",
                    border="1px solid #e5e7eb",
                ),
                width="100%",
                max_width="420px",
            ),
            padding_top="10vh",  # Increased padding from the top
            width="100%",  # Ensure center takes full width
        ),
        # Bottom footer (Positioned absolutely)
        rx.box(
            rx.text(
                "TrustWeb Experiment Platform",
                font_size="sm",
                color="#6b7280",
                text_align="center",
                pb="4",
            ),
            position="absolute",
            bottom="0",
            left="0",
            right="0",
            width="100%",
        ),
        bg="#f3f4f6",
        min_height="100vh",
        position="relative",
        padding_bottom="4em",  # Space for the footer
    )


def instructions() -> rx.Component:
    """Instructions component styled to match the provided image."""
    # Define list items for clarity
    section1_items = [
        "An automated Player A will decide how much of their points to send to you.",
        "The amount sent by Player A will be multiplied by 2. This is the amount you (Player B) receive.",
        "You will then decide how much of the received amount to return to Player A. You can return any amount from 0 up to the total amount you received.",
        "Your profit for the round is: Received Amount - Amount Returned.",
        "Player A's profit for the round is: Amount Returned - Amount Sent by A.",
    ]
    section2_items = [
        "You will decide how much of your current balance to send to an automated Player B. You can send up to half of your current balance (Balance / 2, rounded down).",
        "The amount you send will be multiplied by 2 before Player B receives it.",
        "The automated Player B will then decide how much to return to you, based on a consistent strategy determined at the start of the section.",
        "Your balance for the next round is: Your Previous Balance - Amount Sent + Amount Returned.",
        "Your profit for the round is: Amount Returned - Amount Sent.",
        "Player B's profit for the round is: (Amount Sent * 2) - Amount Returned.",
    ]

    # Wrap all content in a single vstack with padding
    content_vstack = rx.vstack(
        # Welcome Section
        rx.hstack(
            rx.icon(tag="info", size=24, color="#3b82f6"),
            rx.vstack(
                rx.heading("Welcome to the Trust Game Experiment!", size="5", weight="bold"),
                rx.text(
                    "Please read the instructions carefully before starting.",
                    size="2",
                    color=COLORS["text_light"],
                ),
                align_items="start",
                spacing="1",
            ),
            spacing="3",
            align="center",
            mb="4",
        ),
        rx.text(
            "In this experiment, you will participate in a two-player game designed to study trust and decision-making. The game consists of two sections, each lasting 7 rounds.",
            size="3",
            color=COLORS["text"],
            mb="4",
        ),
        rx.divider(my="4"),
        # Section 1
        rx.hstack(
            rx.icon(tag="users", size=24, color="#10b981"),
            rx.heading("Section 1: Playing as Player B", size="4", weight="medium"),
            spacing="3",
            align="center",
            mb="3",
        ),
        rx.text(
            "In the first section, you will play the role of Player B. In each round:",
            size="3",
            color=COLORS["text"],
            mb="2",
        ),
        rx.unordered_list(
            *[rx.list_item(item, pl="1em", mb="1") for item in section1_items],
            size="2",
            color=COLORS["text_light"],
            mb="4",
            style={"listStyleType": "disc", "paddingLeft": "1.5em"},
        ),
        rx.divider(my="4"),
        # Section 2
        rx.hstack(
            rx.icon(tag="line_chart", size=24, color="#8b5cf6"),
            rx.heading("Section 2: Playing as Player A", size="4", weight="medium"),
            spacing="3",
            align="center",
            mb="3",
        ),
        rx.text(
            "In the second section, you will play the role of Player A. You start with an initial balance of 20 points. In each round:",
            size="3",
            color=COLORS["text"],
            mb="2",
        ),
        rx.unordered_list(
            *[rx.list_item(item, pl="1em", mb="1") for item in section2_items],
            size="2",
            color=COLORS["text_light"],
            mb="4",
            style={"listStyleType": "disc", "paddingLeft": "1.5em"},
        ),
        rx.divider(my="4"),
        # Goal Section
        rx.hstack(
            rx.icon(tag="target", size=24, color="#f59e0b"),
            rx.heading("Goal", size="4", weight="medium"),
            spacing="3",
            align="center",
            mb="3",
        ),
        rx.text(
            "Your goal in each section is to maximize your own points. Your decisions and the outcomes will be recorded for research purposes. All data is anonymized.",
            size="3",
            color=COLORS["text"],
            mb="4",
        ),
        # Understand Button
        rx.flex(
            rx.button(
                rx.hstack(
                    rx.text("I Understand, Ready to Start"),
                    rx.icon(tag="arrow_right", size=18),
                    spacing="2",
                ),
                on_click=GameState.start_section_1,  # Or appropriate handler
                style=STYLES["button"],
            ),
            justify="end",  # Align button to the right
            width="100%",
            mt="4",
        ),
        padding="20px",
        spacing="4",
        width="100%",
        align_items="stretch",
    )

    return page_container(content_vstack)


def section_1() -> rx.Component:
    """Section 1 component styled as in the attached image."""
    sent = GameState.amount_to_send
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
                    on_change=GameState.set_amount_to_return,
                    type_="number",
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
                "maxWidth": "600px",
                "width": "100%",
                "marginTop": "40px",
            },
        ),
        style={"height": "100vh"},
    )


def stage_transition() -> rx.Component:
    """Stage transition page styled similarly to instructions()."""
    return page_container(
        section_heading(f"Stage {GameState.current_stage} Complete!"),
        rx.text(
            f"You have completed Stage {GameState.current_stage} with Player B ({GameState.player_b_personality}).",
            size="3",
            color=COLORS["text"],
            mb="2",
        ),
        rx.vstack(
            rx.text(
                f"\U0001f4b0 Your current balance: {GameState.player_a_balance}",
                size="3",
                color=COLORS["text_light"],
            ),
            rx.text(
                f"\U0001f4b5 Your total profit so far: {GameState.player_a_profit}",
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
            on_click=GameState.start_next_stage,
        ),
        # Apply consistent padding within the card
        padding="20px",
    )


def section_2() -> rx.Component:
    """Section 2 component styled similarly to section_1()."""
    balance = GameState.player_a_balance
    max_send = GameState.max_send_amount
    round_str = GameState.round_str
    # Define the main vstack content first for clarity
    section_content = rx.vstack(
        # Header: Section title and round info
        rx.hstack(
            rx.heading(
                "\U0001f4c8 Section 2: You are Player A", size="6", style={"fontWeight": 600}
            ),
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
            type_="number",
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
    """Transition page between Section 1 and Section 2, styled like instructions()."""
    # Wrap all content in a single vstack with padding
    content_vstack = rx.vstack(
        section_heading("Section 1 Complete!"),
        rx.text(
            "You have completed the tutorial section where you played as Player B.",
            size="3",
            color=COLORS["text"],
            mb="3",
        ),
        rx.text(
            "Now, you will play as Player A in Section 2.",
            size="3",
            color=COLORS["text"],
            mb="4",
            weight="medium",
        ),
        rx.box(
            rx.heading(
                "Section 2 Reminders:",
                size="4",
                weight="medium",
                mb="2",
                color=COLORS["text_light"],
            ),
            rx.unordered_list(
                rx.list_item("You will start with 20 currency units.", pl="1em", mb="1"),
                rx.list_item(
                    "You can send up to 50% of your current balance in each round.",
                    pl="1em",
                    mb="1",
                ),
                rx.list_item("The amount you send will be multiplied by 2.", pl="1em", mb="1"),
                rx.list_item(
                    "Player B (AI) will decide how much to return based on a consistent personality.",
                    pl="1em",
                    mb="1",
                ),
                rx.list_item("Your profit = Amount returned - Amount sent.", pl="1em", mb="1"),
                rx.list_item(
                    "Player B's profit = (Amount Sent * 2) - Amount returned.", pl="1em", mb="1"
                ),
                rx.list_item(f"The section consists of {NUM_ROUNDS} rounds.", pl="1em", mb="1"),
                size="2",
                color=COLORS["text_light"],
                style={"listStyleType": "disc", "paddingLeft": "1.5em"},
            ),
            bg=COLORS["background"],
            padding="4",
            border_radius="md",
            width="100%",
            mb="6",
            border=f"1px solid {COLORS['border']}",
        ),
        primary_button(
            rx.hstack(
                rx.text("I'm Ready for Section 2"),
                rx.icon(tag="arrow_right", size=18),
                spacing="2",
            ),
            on_click=GameState.start_section_2,
        ),
        # Apply padding to this wrapper vstack
        padding="20px",
        spacing="4",
        width="100%",
        align_items="stretch",
    )

    # Pass the single wrapped vstack to page_container
    return page_container(content_vstack)


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
