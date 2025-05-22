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
            # Left: App title - now a link to the landing page
            rx.link(
                rx.heading("TrustWeb", size="6", color="#333"),
                href="/",
                _hover={"text_decoration": "none"},  # Optional: remove underline on hover
            ),
            # Center: Navigation tabs
            rx.spacer(),
            rx.cond(
                AuthState.is_authenticated,
                rx.hstack(
                    rx.link(
                        rx.hstack(
                            rx.icon("pencil"),
                            rx.text("기본정보입력"),
                        ),
                        href="/app/demography",
                        color="#333",
                        padding="0.5em 1em",
                        border_radius="md",
                        _hover={"bg": "#f0f0f0"},
                    ),
                    rx.link(
                        rx.hstack(
                            rx.icon("file_text"),
                            rx.text("설문지작성"),
                        ),
                        href="/app/questionnaire",
                        color="#333",
                        padding="0.5em 1em",
                        border_radius="md",
                        _hover={"bg": "#f0f0f0"},
                    ),
                    rx.link(
                        rx.hstack(
                            rx.icon("bell"),
                            rx.text("공공재게임"),
                        ),
                        href="/app/instructions?game=public_goods",
                        color="#333",
                        padding="0.5em 1em",
                        border_radius="md",
                        _hover={"bg": "#f0f0f0"},
                    ),
                    rx.link(
                        rx.hstack(
                            rx.icon("bell"),
                            rx.text("신뢰게임"),
                        ),
                        href="/app/instructions?game=section1",
                        color="#333",
                        padding="0.5em 1em",
                        border_radius="md",
                        _hover={"bg": "#f0f0f0"},
                    ),
                    rx.link(
                        rx.hstack(
                            rx.icon("activity"),
                            rx.text("결과보기"),
                        ),
                        href="/app/results",
                        color="#333",
                        padding="0.5em 1em",
                        border_radius="md",
                        _hover={"bg": "#f0f0f0"},
                    ),
                    spacing="4",
                ),
            ),
            rx.spacer(),
            # Right: User info and login/logout
            rx.cond(
                AuthState.is_authenticated,
                rx.hstack(
                    rx.button(
                        rx.icon("log_out"),
                        rx.text("Log out"),
                        on_click=AuthState.logout,
                        size="3",
                        color_scheme="gray",
                    ),
                    spacing="4",
                ),
                rx.button(
                    "로그인",
                    on_click=AuthState.open_login_modal,
                    size="3",
                    color_scheme="orange",
                ),
            ),
            width="100%",
            padding="1em",
            bg="#fefaef",
            box_shadow="0 4px 16px 0 rgba(0,0,0,0.12)",
            position="relative",
            z_index=1,
        ),
        # Main content
        rx.box(
            content,
            flex="1",
            width="100%",
            padding="0",
            height="auto",
            overflow_y="visible",
            style={"marginTop": "3em"},
        ),
        # Login modal (global, so it works from nav)
        rx.cond(
            AuthState.show_login_modal,
            rx.dialog.root(
                rx.dialog.content(
                    # New close button at the top right
                    rx.dialog.close(
                        rx.icon(
                            tag="x",
                            style={
                                "cursor": "pointer",
                                "position": "absolute",
                                "top": "0.8rem",
                                "right": "0.8rem",
                                "color": "#AAAAAA",  # Light gray color for the X icon
                                "_hover": {"color": "#333333"},  # Darker on hover
                            },
                            on_click=AuthState.close_login_modal,  # Ensure modal closes
                        )
                    ),
                    # login_form() is here
                    __import__("Trust_Web.components.login_form", fromlist=["login_form"]).login_form(),
                    # Removed the old close button from the bottom
                    # rx.dialog.close(
                    #     rx.button("닫기", on_click=AuthState.close_login_modal, style={"marginTop": "1em"})
                    # ),
                    style={
                        "padding": "2em",
                        "borderRadius": "1em",
                        "minWidth": "400px",
                        "maxWidth": "400px",
                        "position": "relative",  # Needed for absolute positioning of the close button
                        "bg": "#fefaef",  # Added requested background color
                    },
                ),
                open=AuthState.show_login_modal,
                on_open_change=AuthState.set_login_modal_state,
            ),
        ),
        # Footer
        rx.box(
            rx.vstack(
                rx.text(
                    "© 2025 TrustLab. All rights reserved.",
                    color="#fff",
                    font_size="1.6rem",
                    text_align="center",
                    font_weight="500",
                ),
                width="100%",
                align_items="center",
            ),
            width="100%",
            padding="1.5em 0 1em 0",
            border_top=None,
            # color_scheme="gray",
            bg="#64748b",
            # border_radius="0 0 2em 2em",
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
