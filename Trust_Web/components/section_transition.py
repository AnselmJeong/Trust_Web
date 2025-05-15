import reflex as rx
from Trust_Web.trust_game_state import TrustGameState, NUM_ROUNDS
from .common_styles import COLORS, page_container, section_heading, primary_button


def section_transition() -> rx.Component:
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
            on_click=TrustGameState.start_section_2,
        ),
        # Apply padding to this wrapper vstack
        padding="20px",
        spacing="4",
        width="100%",
        align_items="stretch",
    )

    # Pass the single wrapped vstack to page_container
    return page_container(content_vstack)
