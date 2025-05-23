import reflex as rx
from Trust_Web.trust_game_state import TrustGameState
from .common_styles import COLORS, page_container, section_heading, primary_button


def stage_transition() -> rx.Component:
    """Stage transition page styled similarly to section1/2, with a summary table."""
    return rx.center(
        rx.box(
            rx.vstack(
                # Header
                rx.hstack(
                    rx.icon(tag="user", mr=2),
                    rx.heading(f"스테이지 {TrustGameState.current_stage} 완료!", size="7"),
                    rx.spacer(),
                    rx.text(f"상대방: {TrustGameState.player_b_personality}", color_scheme="gray", font_weight="bold"),
                    justify="between",
                    align_items="center",
                    width="100%",
                ),
                rx.divider(),
                rx.text(
                    "이번 스테이지 동안 당신의 투자 및 수익 요약입니다.",
                    size="4",
                    color_scheme="gray",
                    margin_bottom="1em",
                ),
                rx.center(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("항목"),
                                rx.table.column_header_cell("합계", text_align="center"),
                            )
                        ),
                        rx.table.body(
                            rx.table.row(
                                rx.table.cell(rx.text("투자한 포인트 합계", color="#6b7280", size="3")),
                                rx.table.cell(
                                    rx.text(TrustGameState.stage_total_invested, size="6", text_align="center")
                                ),
                            ),
                            rx.table.row(
                                rx.table.cell(rx.text("돌려받은 포인트 합계", color="#6b7280", size="3")),
                                rx.table.cell(
                                    rx.text(TrustGameState.stage_total_returned, size="6", text_align="center")
                                ),
                            ),
                            rx.table.row(
                                rx.table.cell(rx.text("순이익", color="#6b7280", size="3")),
                                rx.table.cell(rx.text(TrustGameState.stage_net_payoff, size="6", text_align="center")),
                            ),
                            rx.table.row(
                                rx.table.cell(rx.text("잔고 (스테이지 종료 시점)", color="#6b7280", size="3")),
                                rx.table.cell(rx.text(TrustGameState.stage_end_balance, size="6", text_align="center")),
                            ),
                        ),
                        width="340px",
                        margin_y="2",
                        size="1",
                        variant="ghost",
                    ),
                    width="100%",
                ),
                rx.text(
                    rx.cond(
                        TrustGameState.is_last_stage,
                        "모든 스테이지가 완료되었습니다! 실험의 최종 결과를 확인하세요.",
                        "다음 스테이지에 도전하세요!",
                    ),
                    size="3",
                    color=COLORS["text"],
                    mb="6",
                    weight="medium",
                ),
                rx.cond(
                    TrustGameState.is_last_stage,
                    primary_button(
                        rx.text("최종 결과 보기"),
                        on_click=lambda: rx.redirect("/app/final"),
                    ),
                    primary_button(
                        rx.text("다음 스테이지로 이동"),
                        on_click=TrustGameState.start_next_stage,
                    ),
                ),
                spacing="4",
                align_items="stretch",
            ),
            style={
                "background": "white",
                "borderRadius": "12px",
                "boxShadow": "0 2px 8px 0 rgba(0,0,0,0.07)",
                "padding": "32px 32px 16px 32px",
                "maxWidth": "600px",
                "width": "100%",
            },
        ),
    )
