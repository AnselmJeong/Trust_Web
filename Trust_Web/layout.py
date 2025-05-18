import reflex as rx

# from Trust_Web.trust_game_state import TrustGameState # Removed
from .authentication import AuthState  # Changed to direct relative import


def layout(content: rx.Component) -> rx.Component:
    """
    Wraps content with a consistent header and footer.
    The header includes navigation tabs and user information.
    The footer includes developer credit.
    """
    return rx.vstack(
        # Header
        rx.hstack(
            # Left: App title
            rx.heading("TrustWeb", size="6", color="#333"),
            # Center: Navigation tabs
            rx.spacer(),
            rx.hstack(
                rx.link(
                    rx.hstack(
                        rx.icon("pencil"),
                        rx.text("Demographic"),
                    ),
                    href="/app/demographic",
                    color="#333",
                    padding="0.5em 1em",
                    border_radius="md",
                    _hover={"bg": "#f0f0f0"},
                ),
                rx.link(
                    rx.hstack(
                        rx.icon("file_text"),
                        rx.text("Questionnaire"),
                    ),
                    href="/app/questionnaire",
                    color="#333",
                    padding="0.5em 1em",
                    border_radius="md",
                    _hover={"bg": "#f0f0f0"},
                ),
                rx.link(
                    rx.hstack(
                        rx.icon("activity"),
                        rx.text("Results"),
                    ),
                    href="/app/results",
                    color="#333",
                    padding="0.5em 1em",
                    border_radius="md",
                    _hover={"bg": "#f0f0f0"},
                ),
                rx.link(
                    rx.hstack(
                        rx.icon("bell"),
                        rx.text("Updates"),
                    ),
                    href="/app/updates",
                    color="#333",
                    padding="0.5em 1em",
                    border_radius="md",
                    _hover={"bg": "#f0f0f0"},
                ),
                spacing="4",
            ),
            rx.spacer(),
            # Right: User info and logout
            rx.hstack(
                rx.text(AuthState.user_email),  # Changed to AuthState
                rx.button(
                    rx.icon("log_out"),
                    rx.text("Log out"),
                    on_click=AuthState.logout,  # Changed to AuthState
                    size="1",
                    color_scheme="gray",
                ),
                spacing="4",
            ),
            width="100%",
            padding="1em",
            border_bottom="1px solid #e2e8f0",
            bg="#f8f9fa",
        ),
        # Main content
        rx.box(
            content,
            flex="1",
            width="100%",
            padding="2em 0",
            min_height="calc(100vh - 140px)",  # Adjust based on header/footer height
        ),
        # Footer
        rx.box(
            rx.text(
                "Developed by Anselm Jeong",
                color="#666",
                text_align="right",
                padding_right="2em",
            ),
            width="100%",
            padding="1em",
            border_top="1px solid #e2e8f0",
            bg="#f8f9fa",
        ),
        width="100%",
        min_height="100vh",
        spacing="0",
    )


def auth_layout(content: rx.Component) -> rx.Component:
    """
    Special layout for authenticated pages.
    If user is not authenticated, redirects to login page.
    """
    return rx.cond(
        AuthState.is_authenticated,  # Changed to AuthState
        layout(content),
        rx.box(
            rx.redirect("/"),  # Changed to redirect to root for login
            rx.spinner(size="3"),
            rx.text("Redirecting to login..."),
            align="center",
            justify="center",
            height="100vh",
        ),
    )
