import reflex as rx
from .common_styles import page_container, section_heading, primary_button, COLORS
from ..authentication import AuthState


def landing_page() -> rx.Component:
    """Landing page component for the website root."""
    return page_container(
        rx.vstack(
            section_heading("당신은 과연 타인을 얼마나 믿을 수 있나요?", style={"font_size": "2.5rem", "color": COLORS["text"]}),
            rx.text(
                "연구에 참여하여 나의 신뢰 감각을 시험해보세요.",
                style={"font_size": "1.25rem", "color": COLORS["primary"], "mb": "2"},
            ),
            rx.hstack(
                # Illustration placeholder (replace with image if available)
                rx.box(
                    rx.icon("handshake", size=64, color=COLORS["primary"]),
                    style={"min_width": "120px", "min_height": "120px", "display": "flex", "align_items": "center", "justify_content": "center", "bg": COLORS["background"]},
                ),
                rx.box(
                    rx.text(
                        "우리는 모두 타인과 관계를 맺어 함께 살아가고자 합니다. 하지만 누군가에게는 관계를 맺는 것이 너무나 어려운 일입니다.\n\n모든 관계 맺기의 시작은 타인에 대한 기본적 신뢰로부터 출발합니다.\n\n이에 저희 연구진은 대인관계를 어려워하는 분들의 타인에 대한 신뢰 정도를 살펴보고자 합니다.",
                        style={"color": COLORS["text_light"], "font_size": "1rem", "white_space": "pre-line"},
                    ),
                    style={"ml": "2"},
                ),
                spacing="6",
                width="100%",
                align_items="center",
                mb="4",
            ),
            rx.divider(),
            rx.box(
                rx.hstack(
                    rx.icon("info", color="#e53e3e"),
                    rx.text("연구 참여를 통해 무엇을 하게 되나요", style={"font_weight": 600, "font_size": "1.1rem"}),
                    spacing="2",
                ),
                rx.text(
                    "간단한 신뢰 게임과 짧은 설문을 통해 나의 신뢰 성향과 반응 패턴을 확인할 수 있습니다.\n여러분의 참여는 신뢰 현상과 현대 사회의 관계를 이해하는 단서가 됩니다.\n수집된 자료는 연구 목적으로만 사용되며, 익명 처리로 안전하게 보호됩니다.\n개인 신변 정보는 일절 수집하지 않으며, 참여자 개인 정보는 철저히 보호됩니다.",
                    style={"color": COLORS["text_light"], "font_size": "0.98rem", "white_space": "pre-line", "mt": "2"},
                ),
                style={"bg": COLORS["background"], "border_radius": "lg", "p": "5", "mt": "4", "mb": "4"},
            ),
            rx.center(
                primary_button(
                    "회원가입/로그인",
                    on_click=AuthState.open_login_modal,
                    style={"max_width": "220px", "font_size": "1.1rem"},
                ),
                width="100%",
                mt="2",
            ),
        ),
        padding_top="6em",
        padding_x="2em",
    ) 