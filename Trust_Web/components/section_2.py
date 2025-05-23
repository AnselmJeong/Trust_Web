import reflex as rx
from Trust_Web.trust_game_state import TrustGameState, NUM_ROUNDS
from .common_styles import COLORS, STYLES, primary_button # Removed unused COLORS
from .stage_transition import stage_transition
from .ui_helpers import GameSectionCard # Import the new component


def section_2() -> rx.Component:
    """Section 2 component, refactored to use GameSectionCard."""
    balance = TrustGameState.player_a_balance
    max_send = TrustGameState.max_send_amount
    round_str = TrustGameState.round_str
    # Assuming shuffled_profiles is populated and its length is the total number of stages.
    # If TrustGameState.shuffled_profiles can be empty, add a check or ensure it's always populated before this page.
    total_stages = TrustGameState.shuffled_profiles.length() # Access length of Var[List]
    stage_info_text = rx.text(
        f" 상대 {TrustGameState.current_stage + 1} / {total_stages} - {round_str}",
        color_scheme="gray",
        font_weight="bold"
    )
    
    decision_submitted = (
        TrustGameState.is_decision_submitted if hasattr(TrustGameState, "is_decision_submitted") else False
    )

    # Content for the GameSectionCard
    game_content = [
        rx.text(
            "당신은 투자자입니다. 상대방(수탁자)에게 얼마를 투자할지 결정하세요.", # Changed text to reflect Player A role
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
                        rx.heading(balance, size="8", style={"color": STYLES["text"] if "text" in STYLES else "#374151"}), # Use common style if available
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
                        style={"background": COLORS.get("background_light", "#f9fafb"), "borderRadius": "8px", "padding": "12px 0"},
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
                        style={"background": COLORS.get("background", "#f3f4f6"), "borderRadius": "8px", "padding": "12px 0"},
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
            # Assuming plum_button is available or use rx.button with custom style
            rx.button( # Fallback to rx.button if plum_button is not defined or imported
                "다음 라운드로 넘어갑니다",
                width="100%",
                size="3",
                on_click=[
                    TrustGameState.go_to_next_round,
                ],
                color_scheme="plum", # Keep original styling if plum_button not used
            ),
        ),
    ]

    # The main structure using GameSectionCard
    section_card_content = GameSectionCard(
        title="신뢰 게임 (투자자 역할)", # Corrected title for Player A
        icon_name="user", # Or "users"
        header_extras=stage_info_text,
        progress_value=TrustGameState.current_round,
        progress_max=NUM_ROUNDS,
        *game_content, # Unpack the list of children
        # Apply the specific styling from the old rx.box to this GameSectionCard instance
        style={
            "background": "white",
            "borderRadius": "12px",
            "boxShadow": "0 2px 8px 0 rgba(0,0,0,0.07)",
            "padding": "32px", # Simplified padding, adjust if specific top/bottom needed
            "maxWidth": "600px", # Already default in GameSectionCard but explicit here
            "width": "100%",
        }
    )

    return rx.cond(
        TrustGameState.is_stage_transition,
        stage_transition(),
        rx.center(section_card_content), # Center the GameSectionCard
    )
