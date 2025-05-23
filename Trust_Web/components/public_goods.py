import reflex as rx
from Trust_Web.public_goods_state import (
    PublicGoodState,
    TOTAL_ROUNDS,
    NUM_COMPUTER_PLAYERS,
    MULTIPLIER,
)
# from Trust_Web.trust_game_state import TrustGameState # Removed unused import
from .common_styles import STYLES, primary_button, plum_button, COLORS 
from .ui_helpers import GameSectionCard # Import the new component


def public_goods_game_component() -> rx.Component:
    """UI component for the Public Goods Game, refactored to use GameSectionCard."""

    header_extras_content = rx.text(
        rx.text(f"{PublicGoodState.display_round_number} / {TOTAL_ROUNDS} 라운드", font_weight="bold"),
        color_scheme="gray",
    )

    game_content = [
        rx.text(
            f"참가자: 당신을 포함해서 {NUM_COMPUTER_PLAYERS + 1}명",
            size="3",
            color_scheme="gray",
        ),
        rx.cond(
            ~PublicGoodState.game_finished,
            rx.cond(
                ~PublicGoodState.game_played,
                rx.vstack(
                    rx.center(
                        rx.vstack(
                            rx.text("현재 잔고", size="4", color_scheme="gray"),
                            rx.heading(PublicGoodState.human_balance, size="8", style={"color": STYLES.get("text", "#374151")}), # Use common style
                            align_items="center",
                            text_align="center",
                        ),
                    ),
                    rx.divider(),
                    rx.text(
                        "공공재에 얼마나 기부하시겠습니까?",
                        size="5",
                        color_scheme="plum",
                        font_weight="bold",
                    ),
                    rx.input(
                        id="public_goods_input",
                        placeholder=f"0 ~ {PublicGoodState.human_balance // 2}",
                        on_change=PublicGoodState.set_human_contribution,
                        type="number",
                        **STYLES["input"],
                    ),
                    rx.cond(
                        PublicGoodState.contribution_error != "",
                        rx.text(PublicGoodState.contribution_error, color_scheme="red", size="2"),
                    ),
                    align_items="stretch",
                    spacing="2",
                    width="100%",
                ),
            ),
        ),
        rx.cond(
            PublicGoodState.game_finished,
            rx.vstack(
                rx.heading("공공재 게임이 끝났습니다.", size="7"),
                rx.heading("대단히 수고하셨습니다.", size="5"),
                plum_button(
                    "이제 신뢰 게임으로 넘어갑니다",
                    on_click=lambda: rx.redirect("/app/instructions?game=section1"),
                    style={"margin_top": "1.5rem"},
                ),
                align_items="center",
                padding="2rem",
            ),
            rx.cond(
                ~PublicGoodState.game_played,
                primary_button(
                    "결정 제출",
                    on_click=[
                        PublicGoodState.play_game,
                        rx.set_value("public_goods_input", ""),
                    ],
                    disabled=(PublicGoodState.contribution_error != ""),
                ),
            ),
        ),
        rx.cond(
            PublicGoodState.game_played,
            rx.vstack(
                rx.hstack(
                    rx.text("내 기부액", size="2", color="#ab4abb"),
                    rx.text("상대편 기부액", size="2", color_scheme="gray"),
                    spacing="9",
                    justify="between",
                    width="50%",
                ),
                rx.hstack(
                    rx.box(
                        rx.text(PublicGoodState.human_contribution, font_size="1.5rem", color=COLORS["white"], font_weight="bold"),
                        bg="#ab4abb", # Specific color
                        border_radius="md",
                        width="40px",
                        height="40px",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        box_shadow="0 2px 8px 0 #d1432b30",
                        margin_right="1.2em",
                    ),
                    rx.foreach(
                        PublicGoodState.computer_contributions,
                        lambda c: rx.box(
                            rx.text(c, font_size="1.5rem", color="#222", font_weight="bold"), # Specific color
                            bg=COLORS["white"],
                            border_radius="md",
                            width="40px",
                            height="40px",
                            display="flex",
                            align_items="center",
                            justify_content="center",
                            box_shadow="0 2px 8px 0 #facc1530",
                            margin_right="1em",
                        ),
                    ),
                    align_items="center",
                    spacing="2",
                ),
                margin_y="1em",
                align_items="center",
                width="100%",
            ),
        ),
        rx.cond(
            PublicGoodState.game_played,
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.text("투자 총액", size="2", color_scheme="gray"),
                        rx.heading(PublicGoodState.total_contribution.to_string(), size="8"),
                        align_items="center",
                        flex_grow=1,
                        text_align="center",
                    ),
                    rx.vstack(
                        rx.text("총수익", size="2", color_scheme="gray"),
                        rx.heading(PublicGoodState.multiplied_pool_str, size="8"),
                        align_items="center",
                        flex_grow=1,
                        text_align="center",
                    ),
                    rx.vstack(
                        rx.text("당신의 배당", size="2", color_scheme="gray"),
                        rx.heading(PublicGoodState.per_share_str, size="8"),
                        align_items="center",
                        flex_grow=1,
                        text_align="center",
                    ),
                    justify="between",
                    width="100%",
                    spacing="4",
                    padding_y="2",
                ),
                rx.divider(),
                rx.vstack(
                    rx.text("이번 라운드 순수익", size="5", color_scheme="gray"),
                    rx.heading(PublicGoodState.human_payoff_str, size="8"),
                    align_items="center",
                    padding_y="2",
                ),
                rx.text(
                    f"당신의 새로운 잔고: {PublicGoodState.human_balance}",
                    size="5",
                    color_scheme="gray",
                    text_align="center",
                    width="100%",
                ),
                spacing="3",
                width="100%",
                align_items="stretch",
                padding="4",
                border="1px solid #ddd",
                border_radius="md",
                margin_top="4",
            ),
        ),
        rx.cond(
            PublicGoodState.game_played,
            plum_button(
                "다음 라운드로 넘어갑니다",
                on_click=PublicGoodState.prepare_next_round,
            ),
        ),
    ]

    return GameSectionCard(
        title="공공재 게임",
        icon_name="users",
        header_extras=header_extras_content,
        progress_value=PublicGoodState.display_round_number, # Use display_round_number (1-indexed)
        progress_max=TOTAL_ROUNDS,
        *game_content, # Unpack children
        # Apply specific margin from the old rx.card if needed, otherwise defaults from GameSectionCard apply
        margin_top="2em" # Keep the original margin_top
    )
