import reflex as rx
from Trust_Web.trust_game_state import TrustGameState, NUM_ROUNDS
from .common_styles import COLORS, STYLES, primary_button
from .stage_transition import stage_transition


def section_2() -> rx.Component:
    """Section 2 component styled to match section_1, with stage info."""
    balance = TrustGameState.player_a_balance
    max_send = TrustGameState.max_send_amount
    round_str = TrustGameState.round_str
    stage_str = f"Stage {TrustGameState.current_stage + 1} / 4"
    decision_submitted = (
        TrustGameState.is_decision_submitted if hasattr(TrustGameState, "is_decision_submitted") else False
    )
    section_content = rx.vstack(
        # Header: Icon, Title, Stage, Round info
        rx.hstack(
            rx.icon(tag="user", mr=2),
            rx.heading("신뢰 게임 (수탁자 역할)", size="7"),
            rx.spacer(),
            rx.text(stage_str, color_scheme="gray", font_weight="bold", mr="2"),
            rx.text(round_str, color_scheme="gray", font_weight="bold"),
            justify="between",
            align_items="center",
            width="100%",
        ),
        rx.progress(
            value=TrustGameState.current_round,
            max=NUM_ROUNDS,
            width="100%",
            color_scheme="orange",
            height="sm",
            border_radius="md",
        ),
        rx.text(
            "당신은 수탁자입니다. 수신자에게 얼마를 투자할지 결정하세요.",
            size="3",
            color_scheme="gray",
        ),
        rx.divider(),
        rx.cond(
            ~decision_submitted,
            rx.fragment(
                rx.center(
                    rx.vstack(
                        rx.text("현재 잔고", size="2", color_scheme="gray"),
                        rx.heading(balance, size="8", style={"color": "#374151"}),
                        align_items="center",
                        text_align="center",
                    ),
                ),
                rx.text(
                    "수신자에게 투자할 금액을 입력하세요",
                    size="5",
                    color_scheme="plum",
                    font_weight="bold",
                    margin_top="1.5em",
                ),
                rx.input(
                    id="amount_input_s2",
                    placeholder=f"0 ~ {max_send}",
                    on_change=TrustGameState.set_amount_to_send,
                    type="number",
                    **STYLES["input"],
                    disabled=decision_submitted,
                ),
            ),
        ),
        # 결정 제출 후 결과 테이블
        rx.cond(
            decision_submitted,
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.text("송금한 금액", size="2", color_scheme="gray"),
                        rx.heading(f"{TrustGameState.amount_to_send}", size="8"),
                        align_items="center",
                        flex_grow=1,
                        text_align="center",
                        style={"background": "#f9fafb", "borderRadius": "8px", "padding": "12px 0"},
                    ),
                    rx.vstack(
                        rx.text("돌려받은 금액", size="2", color_scheme="gray"),
                        rx.heading(
                            f"{TrustGameState.amount_to_return}",
                            size="8",
                            font_weight="bold",
                            text_align="center",
                            color_scheme="plum",
                        ),
                        align_items="center",
                        flex_grow=1,
                        text_align="center",
                        style={"background": "#f3f4f6", "borderRadius": "8px", "padding": "12px 0"},
                    ),
                    justify="between",
                    width="100%",
                    spacing="4",
                    padding_y="2",
                    margin_bottom="2rem",
                ),
                rx.center(
                    rx.vstack(
                        rx.center(
                            rx.cond(
                                TrustGameState.player_a_current_round_payoff > 0,
                                rx.heading(
                                    f"당신의 순수익은 {TrustGameState.player_a_current_round_payoff} 포인트 입니다.",
                                    size="5",
                                    font_weight="bold",
                                    color_scheme="gray",
                                    text_align="center",
                                ),
                                rx.text(
                                    f"당신의 순손실은 {TrustGameState.player_a_current_round_payoff} 포인트 입니다.",
                                    size="5",
                                    font_weight="bold",
                                    color_scheme="tomato",
                                    text_align="center",
                                ),
                            ),
                            width="100%",
                        ),
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell(""),
                                    rx.table.column_header_cell("나", text_align="center"),
                                    rx.table.column_header_cell("상대방", text_align="center"),
                                )
                            ),
                            rx.table.body(
                                rx.table.row(
                                    rx.table.cell(rx.text("이번 라운드 순수익", color="#6b7280", size="3")),
                                    rx.table.cell(
                                        rx.text(
                                            TrustGameState.player_a_current_round_payoff,
                                            size="6",
                                            text_align="center",
                                            font_weight="bold",
                                        )
                                    ),
                                    rx.table.cell(
                                        rx.text(
                                            TrustGameState.player_b_current_round_payoff, size="6", text_align="center"
                                        )
                                    ),
                                ),
                                rx.table.row(
                                    rx.table.cell(rx.text("누적된 잔고", color="#6b7280", size="3")),
                                    rx.table.cell(
                                        rx.text(
                                            TrustGameState.player_a_balance,
                                            size="6",
                                            text_align="center",
                                            font_weight="bold",
                                        )
                                    ),
                                    rx.table.cell(
                                        rx.text(TrustGameState.player_b_balance, size="6", text_align="center")
                                    ),
                                ),
                            ),
                            width="320px",
                            margin_y="2",
                            size="1",
                            variant="ghost",
                        ),
                        width="100%",
                    ),
                ),
                align_items="center",
            ),
        ),
        # 결정 제출/다음 라운드 버튼 분기
        rx.cond(
            ~decision_submitted,
            primary_button(
                "결정 제출",
                on_click=TrustGameState.main_algorithm,
            ),
            rx.button(
                "다음 라운드로 넘어갑니다",
                width="100%",
                size="3",
                on_click=[
                    TrustGameState.go_to_next_round,
                    # rx.set_value("amount_input_s2", ""),
                    # rx.set_focus("amount_input_s2"),
                ],
                color_scheme="plum",
            ),
        ),
        spacing="4",
        align_items="stretch",
    )
    return rx.cond(
        TrustGameState.is_stage_transition,
        stage_transition(),
        rx.center(
            rx.box(
                section_content,
                style={
                    "background": "white",
                    "borderRadius": "12px",
                    "boxShadow": "0 2px 8px 0 rgba(0,0,0,0.07)",
                    "padding": "32px 32px 16px 32px",
                    "maxWidth": "600px",
                    "width": "100%",
                },
            ),
        ),
    )
