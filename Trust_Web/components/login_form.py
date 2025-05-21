import reflex as rx
from reflex.vars import Var
from reflex.event import EventSpec
from Trust_Web.trust_game_state import TrustGameState
from .common_styles import COLORS, STYLES
from ..authentication import AuthState

# Styling constants (assuming they are defined elsewhere or replace with actual styles)
PRIMARY_COLOR = "#f97316"
PRIMARY_DARK_COLOR = "#f85a05"
WHITE_COLOR = "white"
BORDER_COLOR = "#e5e7eb"
TEXT_LIGHT_COLOR = "#6b7280"

# Define specific styles for login_form if not fully covered by common_styles
login_form_input_style = {
    **STYLES.get("input", {}),  # Start with common input style
    "mb": "4",  # Override or add specific margin
    "width": "100%",
}

login_form_button_style = {
    **STYLES.get("button", {}),
    "font_size": "md",  # Example override
    "mb": "4",
    "width": "100%",
}


def login_form() -> rx.Component:
    """Login and registration form component."""
    return rx.box(
        rx.vstack(
            rx.heading("연구 참여 로그인", size="7", mb="6", text_align="center"),
            rx.text(
                "연구에 참여해주셔서 감사합니다.\n 계정이 없으시면 회원가입을 진행해주세요.",
                mb="6",
                color=COLORS.get("text_light", "#6b7280"),
                text_align="left",
                style={"white_space": "pre-line"},
            ),
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger("로그인", value="login"),
                    rx.tabs.trigger("회원가입", value="register"),
                    width="100%",
                    justify_content="space_between",  # Use space-between for two items
                    mb="4",
                ),
                rx.tabs.content(
                    rx.vstack(
                        rx.input(
                            placeholder="이메일",
                            value=AuthState.user_email,  # Changed
                            on_change=AuthState.set_user_email,  # Changed
                            type="email",
                            style=login_form_input_style,
                        ),
                        rx.input(
                            placeholder="비밀번호",
                            value=AuthState.password,  # Changed
                            on_change=AuthState.set_password,  # Changed
                            type="password",
                            style=login_form_input_style,
                            on_key_down=AuthState.login_on_enter,
                        ),
                        rx.button(
                            "로그인",
                            on_click=AuthState.login,  # Changed
                            style=login_form_button_style,
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    value="login",
                    min_height="250px",
                ),
                rx.tabs.content(
                    rx.vstack(
                        rx.input(
                            placeholder="이메일",
                            value=AuthState.user_email,  # Changed
                            on_change=AuthState.set_user_email,  # Changed
                            type="email",
                            style=login_form_input_style,
                        ),
                        rx.input(
                            placeholder="비밀번호",
                            value=AuthState.password,  # Changed
                            on_change=AuthState.set_password,  # Changed
                            type="password",
                            style=login_form_input_style,
                            on_key_down=AuthState.login_on_enter,
                        ),
                        rx.input(
                            placeholder="비밀번호 확인",
                            value=AuthState.confirm_password,  # Changed
                            on_change=AuthState.set_confirm_password,  # Changed
                            type="password",
                            style=login_form_input_style,
                            on_key_down=AuthState.register_on_enter,
                        ),
                        rx.button(
                            "회원가입",
                            on_click=AuthState.register,  # Changed
                            style=login_form_button_style,
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    value="register",
                    min_height="250px",
                ),
                default_value="login",
                width="100%",
            ),
            rx.cond(
                AuthState.auth_error != "",  # Changed
                rx.callout.root(
                    rx.callout.icon(rx.icon("circle_alert")),
                    rx.callout.text(AuthState.auth_error),  # Changed
                    color_scheme="red",
                    variant="soft",
                    margin_top="1em",
                    width="100%",
                ),
            ),
            spacing="5",  # Overall spacing for the vstack elements
            width="100%",
        ),
        bg=COLORS.get("white", "white"),
        padding="10",  # Equivalent to p="10" or p_x=10, p_y=10 -> 2.5rem if 1 unit = 0.25rem
        # border_radius="xl",
        # box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        max_width="350px",
        width="100%",
        margin="auto",  # Center the box itself
    )
