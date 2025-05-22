import reflex as rx

# Remove TrustGameState import if not used for other specific logic
# from Trust_Web.trust_game_state import TrustGameState
from Trust_Web.instruction_state import InstructionState  # Import InstructionState from new location
from .common_styles import COLORS, STYLES, page_container, primary_button  # Assuming these are still relevant
from Trust_Web.layout import layout  # Import the main layout
from Trust_Web.trust_game_state import TrustGameState  # 추가: section1 시작 이벤트를 위해 import


def dynamic_instructions_page() -> rx.Component:
    """Dynamic instructions component that loads content based on InstructionState."""

    error_display = rx.cond(
        InstructionState.error_message != "",
        rx.callout.root(
            rx.callout.icon(rx.icon("triangle_alert")),
            rx.callout.text(InstructionState.error_message),
            color_scheme="red",
            variant="soft",
            margin_y="1em",
        ),
        rx.fragment(),  # Empty fragment if no error
    )

    content_vstack = rx.vstack(
        error_display,  # Display error if any
        rx.heading(InstructionState.current_game_title, size="7", weight="bold", text_align="center", mb="2em"),
        rx.cond(
            InstructionState.current_game_rules.length() > 0,
            rx.vstack(
                rx.foreach(
                    InstructionState.current_game_rules,
                    lambda rule, i: rx.box(
                        rx.hstack(
                            rx.text(
                                f"{i + 1}.",
                                color=COLORS["primary"],
                                font_weight="bold",
                                font_size="1.5em",
                                min_width="1.5em",
                            ),
                            rx.text(rule, padding_y="0.5em"),
                            align_items="start",
                            spacing="2",
                        ),
                        border_left=f"4px solid {COLORS['primary']}",
                        padding_x="1em",
                        margin_bottom="0.75em",
                        background_color="#f9fafb",
                    ),
                ),
                spacing="3",
                align_items="stretch",
                width="100%",
                mb="2em",
            ),
            rx.text("No rules available for this game or game not loaded.", text_align="center", color="gray"),
        ),
        rx.flex(
            rx.match(
                InstructionState.current_game_next_page_url,
                (
                    "/app/section1",
                    primary_button(
                        rx.hstack(
                            rx.text(InstructionState.current_game_next_page_text),
                            spacing="2",
                        ),
                        on_click=TrustGameState.start_section_1,
                        color_scheme="orange",
                    ),
                ),
                (
                    "/app/section2",
                    primary_button(
                        rx.hstack(
                            rx.text(InstructionState.current_game_next_page_text),
                            spacing="2",
                        ),
                        on_click=TrustGameState.start_section_2,
                        color_scheme="blue",
                    ),
                ),
                primary_button(
                    rx.hstack(
                        rx.text(InstructionState.current_game_next_page_text),
                        spacing="2",
                    ),
                    on_click=lambda: rx.redirect(InstructionState.current_game_next_page_url),
                    color_scheme="gray",
                ),
            ),
            justify="center",
            width="100%",
            mt="1em",
        ),
        padding="20px",
        spacing="4",
        width="100%",
        max_width="800px",  # Max width for instruction content
        margin_x="auto",  # Center the vstack
        align_items="stretch",
        height="auto",  # Ensure no fixed height
        min_height=None,  # Remove min_height if present
        overflow_y="visible",  # Ensure no forced scroll
    )
    return rx.center(
        rx.box(
            page_container(content_vstack, height="auto", overflow_y="visible"),
            max_width="800px",
            width="100%",
            style={
                "boxShadow": "0 4px 16px 0 rgba(0,0,0,0.12)",
                "borderRadius": "16px",
                "background": "white",
            },
        ),
        width="100%",
    )


# The actual page component that will be routed to /app/instructions
# It needs the on_load handler.
@rx.page(route="/app/instructions", on_load=InstructionState.load_instructions_for_current_page)
def instructions_page() -> rx.Component:
    return layout(dynamic_instructions_page())  # Wrap with main layout
