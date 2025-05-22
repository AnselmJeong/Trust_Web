import reflex as rx
from Trust_Web.trust_game_state import TrustGameState
from ..authentication import AuthState
from .common_styles import page_container, section_heading, primary_button


def final_page() -> rx.Component:
    """Final page component with per-stage summary table."""
    num_stages = 4  # You can also use len(TrustGameState.all_stages_total_invested) if always available
    stage_labels = [f"스테이지 {i + 1}" for i in range(num_stages)]
    return rx.center(
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.icon(tag="star", mr=2),
                    rx.heading("실험이 완료되었습니다!", size="7"),
                    rx.spacer(),
                    justify="between",
                    align_items="center",
                    width="100%",
                ),
                rx.text(
                    "아래는 각 스테이지별 투자 및 수익 요약입니다.",
                    size="4",
                    color_scheme="gray",
                    margin_bottom="1em",
                ),
                rx.center(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("항목"),
                                *[rx.table.column_header_cell(label, text_align="center") for label in stage_labels],
                            )
                        ),
                        rx.table.body(
                            rx.table.row(
                                rx.table.cell(rx.text("투자한 포인트 합계", color="#6b7280", size="3")),
                                rx.foreach(
                                    TrustGameState.all_stages_total_invested,
                                    lambda val: rx.table.cell(rx.text(val, size="6", text_align="center")),
                                ),
                            ),
                            rx.table.row(
                                rx.table.cell(rx.text("돌려받은 포인트 합계", color="#6b7280", size="3")),
                                rx.foreach(
                                    TrustGameState.all_stages_total_returned,
                                    lambda val: rx.table.cell(rx.text(val, size="6", text_align="center")),
                                ),
                            ),
                            rx.table.row(
                                rx.table.cell(rx.text("순이익", color="#6b7280", size="3")),
                                rx.foreach(
                                    TrustGameState.all_stages_net_profit,
                                    lambda val: rx.table.cell(rx.text(val, size="6", text_align="center")),
                                ),
                            ),
                            rx.table.row(
                                rx.table.cell(rx.text("잔고 (스테이지 종료 시점)", color="#6b7280", size="3")),
                                rx.foreach(
                                    TrustGameState.all_stages_end_balance,
                                    lambda val: rx.table.cell(rx.text(val, size="6", text_align="center")),
                                ),
                            ),
                        ),
                        width="100%",
                        margin_y="2",
                        size="1",
                        variant="ghost",
                    ),
                    width="100%",
                ),
                rx.heading(
                    "연구에 참여해주셔서\n다시 한번 감사드립니다!",
                    size="7",
                    color_scheme="gray",
                    margin_top="2em",
                    style={"white-space": "pre-line"},
                    text_align="center",
                    line_height="2.5rem",
                ),
                primary_button("처음으로", on_click=lambda: rx.redirect("/")),
                spacing="4",
                align_items="stretch",
            ),
            style={
                "background": "white",
                "borderRadius": "12px",
                "boxShadow": "0 2px 8px 0 rgba(0,0,0,0.07)",
                "padding": "32px 32px 16px 32px",
                "maxWidth": "800px",
                "width": "100%",
            },
        ),
    )
