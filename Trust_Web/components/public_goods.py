import reflex as rx
from Trust_Web.public_goods_state import (
    PublicGoodState,
    TOTAL_ROUNDS,
    NUM_COMPUTER_PLAYERS,
    MULTIPLIER,
)
from Trust_Web.trust_game_state import TrustGameState
from .common_styles import STYLES


def public_goods_game_component() -> rx.Component:
    """UI component for the Public Goods Game."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon(tag="users", mr=2),
                rx.heading("공공재 게임", size="7"),
                rx.spacer(),
                rx.text(
                    rx.text(f"{PublicGoodState.display_round_number} / {TOTAL_ROUNDS} 라운드", font_weight="bold"),
                    color_scheme="gray",
                ),
                justify="between",
                align_items="center",
                width="100%",
            ),
            rx.progress(
                value=PublicGoodState.current_round + 1,
                max=TOTAL_ROUNDS,
                width="100%",
                color_scheme="orange",
                height="sm",
                border_radius="md",
            ),
            rx.text(
                f"참가자: 당신을 포함해서 {NUM_COMPUTER_PLAYERS + 1}명",
                size="3",
                color_scheme="gray",
            ),
            rx.center(
                rx.vstack(
                    rx.text("현재 잔고", size="4", color_scheme="gray"),
                    rx.heading(PublicGoodState.human_balance, size="8", style={"color": "#374151"}),
                    align_items="center",
                    text_align="center",
                ),
            ),
            rx.divider(),
            rx.cond(
                ~PublicGoodState.game_finished,
                rx.cond(
                    ~PublicGoodState.game_played,
                    rx.vstack(
                        rx.text(
                            "공공재에 얼마나 기부하시겠습니까?",
                            size="5",
                            color_scheme="plum",
                            font_weight="bold",
                        ),
                        rx.input(
                            id="public_goods_input",
                            placeholder=f"0 ~ {PublicGoodState.human_balance // 2}",
                            # value=PublicGoodState.human_contribution.to_string(),
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
                    rx.button(
                        "이제 신뢰 게임으로 넘어갑니다",
                        on_click=lambda: rx.redirect("/app/instructions?game=section1"),
                        width="100%",
                        size="3",
                        color_scheme="plum",
                        margin_top="1.5rem",
                    ),
                    align_items="center",
                    padding="2rem",
                ),
                rx.cond(
                    PublicGoodState.game_played,
                    rx.button(
                        "다음 라운드로 넘어갑니다",
                        on_click=PublicGoodState.prepare_next_round,
                        width="100%",
                        size="3",
                        color_scheme="plum",
                    ),
                    rx.button(
                        "결정 제출",
                        on_click=[
                            PublicGoodState.play_game,
                            rx.set_value("public_goods_input", ""),
                        ],
                        width="100%",
                        size="3",
                        color_scheme="tomato",
                        disabled=(PublicGoodState.contribution_error != ""),
                    ),
                ),
            ),
            rx.cond(
                PublicGoodState.game_played,
                rx.vstack(
                    rx.hstack(
                        rx.heading(
                            f"나의 투자 금액: {PublicGoodState.human_contribution}",
                            size="5",
                            margin_top="4",
                            margin_right="3rem",
                        ),
                        rx.heading(
                            f"상대방의 투자 금액: {PublicGoodState.computer_contributions_str}",
                            size="5",
                            margin_top="4",
                        ),
                        justify="center",
                    ),
                    rx.divider(),
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
            spacing="4",
            align_items="stretch",
        ),
        width="clamp(300px, 80%, 600px)",
        margin_x="auto",
        margin_top="2em",
        padding="6",
    )
