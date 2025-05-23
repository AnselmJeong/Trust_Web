import reflex as rx
from .common_styles import page_container, section_heading, primary_button, COLORS, STYLES # Added STYLES
from ..authentication import AuthState

# New color palette inspired by the provided image
IMAGE_THEME_YELLOW = "#f4f38080"  # A bright, vibrant yellow
IMAGE_THEME_CYAN = "#22D3EE"  # Bright cyan for buttons and accents
IMAGE_THEME_TEXT_DARK = "#111827"  # Very dark gray / almost black for headings
IMAGE_THEME_TEXT_PRIMARY = "#1F2937"  # Dark gray for main body text
IMAGE_THEME_TEXT_SECONDARY = "#4B5563"  # Lighter gray for subtitles or secondary text
IMAGE_THEME_LIGHT_BLUE_BG = "#F0F9FF"  # A very light blue for background accents
IMAGE_THEME_BORDER_YELLOW = "#FACC15"  # A slightly less vibrant yellow for borders/shadows
IMAGE_THEME_DARK_YELLOW_ACCENT = "#E0A80D"  # Slightly darker than BORDER_YELLOW for accents


def landing_page() -> rx.Component:
    """Landing page component with a new theme inspired by the provided image, with '타인' highlighted."""

    hero_section = rx.hstack(
        rx.box(
            # 이미지와 버튼을 겹치기 위해 relative
            rx.image(
                src="/img/hero.png",  # REMINDER: Replace with actual image path
                alt="doubt persist",
                height="auto",  # Adjust size as needed
                width="100%",  # Image takes full width of its parent box
            ),
            primary_button(
                "회원가입/로그인",
                on_click=AuthState.open_login_modal,
                style={
                    "color": COLORS["white"],
                    "font_size": "1.1rem",
                    "padding": "0.8rem 2rem",
                    "border_radius": "md",
                    "width": "auto",
                    "box_shadow": "0 2px 8px 0 #f9731620",
                    "position": "absolute",
                    "bottom": "20%",
                    "left": "78%",
                    "transform": "translateX(-50%)",
                    "z_index": 2,
                },
            ),
            position="relative",
            align_items="center",
            justify_content="center",
            padding_right=["0", "0", "2rem", "2rem"],
            margin_bottom=["2rem", "2rem", "0", "0"],
        ),
        width="100%",
        # padding_y=["1rem", "1.5rem", "2rem"],
        # padding_x=["1rem", "1.5rem", "2rem"],  # Page level padding
        align_items="center",
    )

    divider_line = rx.divider(
        border_color=IMAGE_THEME_BORDER_YELLOW,
        border_width="2px",
        width="100%",
        margin_x="auto",
        margin_y=["1rem", "1.5rem", "2rem"],
    )

    detailed_info_section = rx.hstack(
        rx.vstack(
            section_heading(
                "관계의 시작, 신뢰",
                style={
                    "font_size": ["1.8rem", "2rem", "2.2rem"],
                    "color": IMAGE_THEME_TEXT_DARK,
                    "margin_bottom": "1rem",
                },
            ),
            rx.text(
                "우리는 모두 타인과 관계를 맺어 함께 살아가고자 합니다. 하지만 누군가에게는 관계를 맺는 것이 너무나 어려운 일입니다.\n\n모든 관계 맺기는 타인에 대한 기본적 신뢰로부터 출발합니다.\n\n이에 저희 연구진은 대인관계를 어려워하는 분들을 대상으로 타인에 대한 신뢰 정도를 살펴보고자 합니다.",
                style={
                    "color": IMAGE_THEME_TEXT_PRIMARY,
                    "font_size": "1rem",
                    "white_space": "pre-line",
                    "line_height": "1.7",
                },
            ),
            align_items="flex-start",
            spacing="4",
            width=["100%", "100%", "50%", "50%"],
            padding_right=["0", "0", "2rem", "2rem"],
            order=[2, 2, 1, 1],  # Text first on mobile
        ),
        rx.box(
            # Placeholder for a circular robot image. Replace with your actual image.
            # E.g., rx.image(src="/img/robot_profile.png", ...)
            rx.image(
                src="/img/trust-2.png",  # REMINDER: Replace with actual image path
                alt="Two hands touching each other",
                width="100%",  # Adjust size as needed
                height="auto",
                style={
                    # "border_radius": "full",  # "50%"
                    "object_fit": "cover",
                    # "border": f"6px solid {IMAGE_THEME_YELLOW}",
                    # "box_shadow": f"0 0 25px {IMAGE_THEME_YELLOW}50",
                },
            ),
            width=["100%", "100%", "50%", "50%"],
            align_items="center",
            justify_content="center",
            margin_top=["2rem", "2rem", "0", "0"],
            order=[1, 1, 2, 2],  # Image first on mobile
        ),
        spacing="6",
        width="100%",
        padding_x=["1rem", "1.5rem", "2rem"],
        padding_y=["2rem", "2.5rem", "3rem"],
        align_items="center",
        flex_direction=["column-reverse", "column-reverse", "row", "row"],  # Image above text on mobile
    )

    research_info_section = rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("shield_check", color=IMAGE_THEME_DARK_YELLOW_ACCENT, size=36, mr="3"),
                rx.text(
                    "연구 참여를 통해 무엇을 알 수 있나요?",
                    style={
                        "font_weight": "bold",
                        "font_size": ["1.5rem", "1.6rem", "1.8rem"],
                        "color": IMAGE_THEME_TEXT_DARK,
                    },
                ),
                spacing="3",
                align_items="center",
                mb="1.5rem",
            ),
            rx.text(
                "간단한 신뢰 게임과 짧은 설문을 통해 나의 신뢰 성향과 반응 패턴을 확인할 수 있습니다.\n여러분의 참여는 신뢰 정도와 대인 관계 어려움 사이의 관계를 이해하는 단서가 됩니다.\n수집된 자료는 연구 목적으로만 사용되며, 익명 처리로 안전하게 보호됩니다.\n개인 신변 정보는 일절 수집하지 않으며, 참여자 개인 정보는 철저히 보호됩니다.",
                style={
                    "color": IMAGE_THEME_TEXT_PRIMARY,
                    "font_size": "1rem",
                    "white_space": "pre-line",
                    "line_height": "1.7",
                },
            ),
            align_items="flex-start",
            spacing="3",
        ),
        bg=IMAGE_THEME_YELLOW,  # Added distinct background color for highlight
        border_radius=STYLES["card"]["border_radius"], # Changed to use common style
        padding=["1.5rem", "2rem", "2.5rem"],
        margin_x=["1rem", "1.5rem", "2rem"],
        margin_y=["2rem", "2.5rem", "3rem"],
        box_shadow=f"0 10px 25px -5px {IMAGE_THEME_BORDER_YELLOW}30, 0 8px 10px -6px {IMAGE_THEME_BORDER_YELLOW}20",
    )

    return page_container(
        rx.vstack(
            hero_section,
            divider_line,
            detailed_info_section,
            research_info_section,
            spacing="0",  # Sections manage their own vertical spacing via padding/margins
            width="100%",
            align_items="center",
        ),
        padding_top="0",  # Override default page_container padding if sections handle it
        padding_bottom="2rem",  # Add some space at the very bottom
        padding_x="0",  # Outer container has no horizontal padding, sections will manage their own
        content_width="100%",  # Allow inner card to take full width of the centerer
        content_max_width="1000px",  # Allow inner card to take full max_width of the centerer
        max_width="100vw",  # Ensure it can go full-width if desired
    )
