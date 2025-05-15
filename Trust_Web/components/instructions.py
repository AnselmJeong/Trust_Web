import reflex as rx
from Trust_Web.trust_game_state import TrustGameState
from .common_styles import COLORS, STYLES, page_container


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
                on_click=TrustGameState.start_section_1,  # Or appropriate handler
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
