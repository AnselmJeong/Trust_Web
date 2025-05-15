import reflex as rx
from Trust_Web.trust_game_state import TrustGameState
from .common_styles import COLORS


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
                                on_change=TrustGameState.set_user_email,
                                type="email",
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
                                on_change=TrustGameState.set_password,
                                type="password",
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
                                on_click=TrustGameState.login,
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
                                TrustGameState.auth_error,
                                color="red",
                                font_size="sm",
                                mt="-2",
                                mb="2",
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
                                on_change=TrustGameState.set_user_email,
                                type="email",
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
                                on_change=TrustGameState.set_password,
                                type="password",
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
                                on_change=TrustGameState.set_confirm_password,
                                type="password",
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
                                on_click=TrustGameState.register,
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
                                TrustGameState.auth_error,
                                color="red",
                                font_size="sm",
                                mt="-2",
                                mb="2",
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
