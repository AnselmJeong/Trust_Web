import reflex as rx
from Trust_Web.trust_game_state import TrustGameState, NUM_ROUNDS
from .common_styles import COLORS, STYLES, primary_button, plum_button
from .ui_helpers import GameSectionCard # Import the new component


def section_1() -> rx.Component:
    """Section 1 component styled to match the public goods game theme and using GameSectionCard."""
    sent = TrustGameState.amount_to_send
    received = TrustGameState.received_amount
    round_str = TrustGameState.round_str
    decision_submitted = TrustGameState.is_decision_submitted

    header_extras_content = rx.text(round_str, color_scheme="gray", font_weight="bold")

    return GameSectionCard(
        title="신뢰 게임 (수신자 역할)",
        icon_name="user",
        header_extras=header_extras_content,
        progress_value=TrustGameState.current_round, # Assuming current_round is 1-indexed
        progress_max=NUM_ROUNDS,
        # The vstack content from the original card becomes children here
        # The outer rx.card and its direct rx.vstack for layout are replaced by GameSectionCard
        # Specific card style props like width, margin_x, padding are now handled by GameSectionCard defaults
        # or can be passed as props to GameSectionCard if needed.
        # The inner vstack's spacing and align_items are kept by default in GameSectionCard's vstack.
        # If specific overrides for the content vstack are needed, they'd be applied here or GameSectionCard adjusted.
        rx.cond(
            ~decision_submitted,
            rx.fragment(
                    rx.text(
                        "당신은 수신자입니다. 수탁자가 보낸 포인트 중 얼마를 돌려줄지 결정하세요.",
                        size="3",
                        color_scheme="gray",
                    ),
                    rx.divider(),
                ),
            ),
            # Sent/Received cards (only show before decision submitted)
            rx.cond(
                ~decision_submitted,
                rx.hstack(
                    rx.vstack(
                        rx.text("상대가 보낸 금액", size="2", color_scheme="gray"),
                        rx.heading(sent, size="8", style={"color": COLORS["text"]}), # Changed to COLORS["text"]
                        align_items="center",
                        flex_grow=1,
                        text_align="center",
                        style={"background": COLORS["background_light"], "borderRadius": "8px", "padding": "12px 0"}, # Changed to COLORS["background_light"]
                    ),
                    rx.vstack(
                        rx.text("내가 받은 금액", size="2", color_scheme="gray"),
                        rx.heading(received, size="8", color_scheme="plum"),
                        align_items="center",
                        flex_grow=1,
                        text_align="center",
                        style={"background": "#f3f4f6", "borderRadius": "8px", "padding": "12px 0"},
                    ),
                    justify="between",
                    width="100%",
                    spacing="4",
                    padding_y="2",
                ),
            ),
            rx.divider(),
            # How much to return (only show before decision submitted)
            rx.cond(
                ~decision_submitted,
                rx.fragment(
                    rx.text(
                        "상대방에게 돌려줄 금액을 입력하세요",
                        size="5",
                        color_scheme="plum",
                        font_weight="bold",
                        margin_top="1.5em",
                    ),
                    rx.input(
                        id="amount_input_section1",
                        placeholder=f"0 ~ {received}",
                        on_change=TrustGameState.set_amount_to_return,
                        type="number",
                        **STYLES["input"],
                        disabled=decision_submitted,
                    ),
                ),
            ),
            # 결정 제출 후 payoff/잔고 테이블 표시
            rx.cond(
                decision_submitted,
                rx.fragment(
                    rx.center(
                        rx.cond(
                            TrustGameState.player_b_current_round_payoff > 0,
                            rx.heading(
                                f"상대의 순수익은 {TrustGameState.player_b_current_round_payoff} 포인트 입니다.",
                                size="5",
                                font_weight="bold",
                                color_scheme="gray",
                                text_align="center",
                            ),
                            rx.text(
                                f"상대의 순손실은 {TrustGameState.player_b_current_round_payoff} 포인트 입니다.",
                                size="5",
                                font_weight="bold",
                                color_scheme="tomato",
                                text_align="center",
                            ),
                        ),
                        width="100%",
                    ),
                    rx.center(
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
                                            TrustGameState.player_b_current_round_payoff,
                                            size="6",
                                            font_weight="bold",
                                            text_align="center",
                                        )
                                    ),
                                    rx.table.cell(
                                        rx.text(
                                            TrustGameState.player_a_current_round_payoff,
                                            size="6",
                                            # font_weight="bold",
                                            text_align="center",
                                        )
                                    ),
                                ),
                                rx.table.row(
                                    rx.table.cell(rx.text("누적된 잔고", color="#6b7280", size="3")),
                                    rx.table.cell(
                                        rx.text(
                                            TrustGameState.player_b_balance,
                                            size="6",
                                            font_weight="bold",
                                            text_align="center",
                                        )
                                    ),
                                    rx.table.cell(
                                        rx.text(
                                            TrustGameState.player_a_balance,
                                            size="6",
                                            # font_weight="bold",
                                            text_align="center",
                                        )
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
            ),
            # 결정 제출/다음 라운드 버튼 분기
            rx.cond(
                ~decision_submitted,
                primary_button(
                    "결정 제출",
                    # color_scheme="orange", # Removed color_scheme
                    on_click=TrustGameState.submit_player_b_decision,
                ),
                plum_button( # Changed to plum_button
                    "다음 라운드로 넘어갑니다",
                    on_click=[
                        TrustGameState.go_to_next_round,
                        rx.set_value("amount_input_section1", ""),
                        # rx.set_focus("amount_input_section1"),
                    ],
                    # color_scheme="plum", # Removed color_scheme
                ),
            ),
            rx.divider(),
            # payoffs summary (결정 제출 후에만 보이도록)
            spacing="4",
            align_items="stretch", # This was on the original vstack, GameSectionCard's vstack has this by default
            width="100%" # Ensure the content vstack takes full width within the card
        )
        # Props like width, margin_x, padding="6" from the old rx.card are now defaults in GameSectionCard
        # If specific overrides are needed for THIS instance of GameSectionCard, pass them here:
        # e.g., style={"padding": "custom_padding_value"} or width="desired_width"
    )
