import reflex as rx
from Trust_Web.results_state import ResultsState  # Import ResultsState
from typing import Any


def summary_card(
    title: str, value: rx.Var[Any], unit: str = "", type: str = "user"
) -> rx.Component:
    """Helper function to create a styled summary card."""
    if type == "user":
        color = "#fff6ff"
    else:
        color = "#b487ffb3"

    return rx.box(
        rx.vstack(
            rx.text(
                title,
                font_size="0.8em",
                color_scheme="gray",
                style={"white-space": "pre-line"},
            ),
            rx.hstack(
                rx.heading(value, size="5"),
                rx.text(unit, font_size="1em", color_scheme="gray", margin_left="0.2em")
                if unit
                else rx.fragment(),
                align_items="baseline",
            ),
            align_items="center",  # Center text and heading inside vstack
            spacing="1",
            # color_scheme=color,
        ),
        padding="0.5em",
        border="1px solid #E2E8F0",
        border_radius="lg",
        width="100%",  # Ensure cards take full width in their grid cell
        bg=color,
        # bg="white", # Optional: set a background for cards
        # box_shadow="sm" # Optional: add a subtle shadow
    )


def results_page() -> rx.Component:
    """UI for the experiment results page."""
    return rx.vstack(
        rx.heading(
            "게임 결과 분석", size="8", margin_bottom="0.2em"
        ),  # Main title like the image
        rx.text(
            "다양한 신뢰 게임에서 당신의 성과를 분석하여 보여드립니다.",
            margin_bottom="2em",
            color_scheme="gray",
        ),  # Subtitle
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger(
                    "Public Goods",
                    value="pgg",
                    on_click=ResultsState.load_experiment_data(
                        game_name="public_goods_game"
                    ),
                ),
                rx.tabs.trigger(
                    "Trust Game S1",  # Updated tab titles to match image
                    value="tg1",
                    on_click=ResultsState.load_experiment_data(
                        game_name="trust_game", section_no=1
                    ),
                ),
                rx.tabs.trigger(
                    "Trust Game S2",  # Updated tab titles to match image
                    value="tg2",
                    on_click=ResultsState.load_experiment_data(
                        game_name="trust_game", section_no=2
                    ),
                ),
            ),
            rx.tabs.content(
                rx.vstack(
                    rx.heading(
                        "공공재 게임 결과 분석",
                        size="6",
                        margin_top="1em",
                        margin_bottom="1em",
                    ),
                    rx.cond(
                        ResultsState.current_game_loaded == "public_goods_game",
                        rx.cond(
                            ResultsState.has_pgg_data_to_display,  # Use the new boolean reactive Var
                            rx.vstack(  # Main vstack for cards and chart
                                rx.grid(
                                    # summary_card(
                                    #     "Total Rounds",
                                    #     ResultsState.pgg_overall_summary[
                                    #         "total_rounds"
                                    #     ],
                                    # ),
                                    summary_card(
                                        "당신의\n평균 기부액",
                                        ResultsState.pgg_overall_summary[
                                            "avg_contribution"
                                        ],
                                        unit="포인트",
                                    ),
                                    summary_card(
                                        "당신의\n총 기부액",
                                        ResultsState.pgg_overall_summary[
                                            "total_contribution"
                                        ],
                                        unit="포인트",
                                    ),
                                    summary_card(
                                        "당신의\n평균 순수익",
                                        ResultsState.pgg_overall_summary["avg_payoff"],
                                        unit="포인트",
                                    ),
                                    summary_card(
                                        "당신의\n총 순수익",
                                        ResultsState.pgg_overall_summary[
                                            "total_payoff"
                                        ],
                                        unit="포인트",
                                    ),
                                    columns="repeat(auto-fit, minmax(150px, 1fr))",  # Responsive grid
                                    spacing="4",
                                    width="100%",
                                    max_width="1000px",  # Limit max width of the grid
                                ),
                                # Line Chart for Payoff and Contribution over rounds
                                rx.box(
                                    rx.heading(
                                        "당신의 기부액과 수익",
                                        size="5",
                                        margin_top="2em",
                                        margin_bottom="1em",
                                    ),
                                    rx.recharts.line_chart(
                                        rx.recharts.line(
                                            data_key="payoff",
                                            name="당신의 수익",
                                            stroke="#8884d8",
                                            type="monotone",
                                        ),
                                        rx.recharts.line(
                                            data_key="contribution",
                                            name="당신의 기부액",
                                            stroke="#82ca9d",
                                            type="monotone",
                                        ),
                                        rx.recharts.x_axis(
                                            data_key="round_number", name="Round"
                                        ),
                                        rx.recharts.y_axis(name="Points"),
                                        rx.recharts.cartesian_grid(
                                            stroke_dasharray="3 3"
                                        ),
                                        rx.recharts.graphing_tooltip(),
                                        rx.recharts.legend(),
                                        data=ResultsState.pgg_round_summary,  # Use the per-round summary data
                                        height=400,
                                        width="100%",
                                    ),
                                    border="1px solid #E2E8F0",
                                    border_radius="lg",
                                    padding="1.5em",
                                    margin_top="2em",
                                    width="100%",
                                    max_width="1000px",
                                ),
                                spacing="6",  # Spacing between grid and chart container
                                align_items="center",
                                width="100%",
                            ),
                            rx.text(
                                "No Public Goods Game data to display. Play the game to see your results."
                            ),
                        ),
                        rx.text(
                            "Click the 'Public Goods' tab to load and view your analysis."
                        ),
                    ),
                    align_items="center",  # Center the heading and grid/text
                    spacing="4",
                    width="100%",
                ),
                value="pgg",
            ),
            rx.tabs.content(
                rx.vstack(
                    rx.heading(
                        "신뢰 게임 (수신자 역할) 결과 분석",
                        size="6",
                        margin_top="1em",
                        margin_bottom="1em",
                    ),
                    rx.cond(
                        ResultsState.current_game_loaded == "trust_game",
                        rx.cond(
                            ResultsState.has_tg_section1_data_to_display,
                            rx.fragment(
                                rx.grid(
                                    # summary_card(
                                    #     "Total Rounds",
                                    #     ResultsState.tg_section1_summary[
                                    #         "total_rounds"
                                    #     ],
                                    # ),
                                    summary_card(
                                        "상대가 보낸\n포인트",
                                        ResultsState.tg_section1_summary[
                                            "avg_amount_sent"
                                        ],
                                        unit="포인트",
                                        type="opponent",
                                    ),
                                    # summary_card(
                                    #     "Total Opponent Sent",
                                    #     ResultsState.tg_section1_summary[
                                    #         "total_amount_sent"
                                    #     ],
                                    #     unit="points",
                                    # ),
                                    summary_card(
                                        "당신이 돌려준\n포인트",
                                        ResultsState.tg_section1_summary[
                                            "avg_amount_returned"
                                        ],
                                        unit="포인트",
                                    ),
                                    summary_card(
                                        "상대의\n순수익",
                                        ResultsState.tg_section1_summary[
                                            "player_a_payoff"
                                        ],
                                        unit="포인트",
                                        type="opponent",
                                    ),
                                    summary_card(
                                        "당신의\n순수익",
                                        ResultsState.tg_section1_summary["user_payoff"],
                                        unit="포인트",
                                    ),
                                    summary_card(
                                        "상대방의\n최종 잔액",
                                        ResultsState.tg_section1_summary[
                                            "player_a_balance"
                                        ],
                                        unit="포인트",
                                        type="opponent",
                                    ),
                                    summary_card(
                                        "당신의\n최종 잔액",
                                        ResultsState.tg_section1_summary[
                                            "user_balance"
                                        ],
                                        unit="포인트",
                                    ),
                                    columns="repeat(auto-fit, minmax(150px, 1fr))",
                                    spacing="4",
                                    width="100%",
                                    max_width="1000px",
                                ),
                                rx.hstack(
                                    rx.box(
                                        rx.heading(
                                            "보낸 포인트와 돌려준 포인트",
                                            size="5",
                                            margin_bottom="1em",
                                        ),
                                        rx.recharts.line_chart(
                                            rx.recharts.line(
                                                data_key="amount_sent",
                                                name="보낸 포인트",
                                                stroke="#7c3aed",
                                                type_="monotone",
                                            ),
                                            rx.recharts.line(
                                                data_key="amount_returned",
                                                name="돌려준 포인트",
                                                stroke="#f43f5e",
                                                type_="monotone",
                                            ),
                                            rx.recharts.x_axis(
                                                data_key="stage_round",
                                                name="Stage-Round",
                                            ),
                                            rx.recharts.y_axis(name="Points"),
                                            rx.recharts.cartesian_grid(
                                                stroke_dasharray="3 3"
                                            ),
                                            rx.recharts.graphing_tooltip(),
                                            rx.recharts.legend(),
                                            data=ResultsState.tg_section1_round_chart_data,
                                            width=500,
                                            height=300,
                                        ),
                                        border="1px solid #E2E8F0",
                                        border_radius="lg",
                                        padding="1.5em",
                                        width="50%",
                                    ),
                                    rx.box(
                                        rx.heading(
                                            "Payoffs Over Rounds",
                                            size="5",
                                            margin_bottom="1em",
                                        ),
                                        rx.recharts.line_chart(
                                            rx.recharts.line(
                                                data_key="user_payoff",
                                                name="당신의 순수익",
                                                stroke="#f43f5e",
                                                type_="monotone",
                                            ),
                                            rx.recharts.line(
                                                data_key="player_a_payoff",
                                                name="상대의 순수익",
                                                stroke="#7c3aed",
                                                type_="monotone",
                                            ),
                                            rx.recharts.x_axis(
                                                data_key="stage_round",
                                                name="Stage-Round",
                                            ),
                                            rx.recharts.y_axis(name="Points"),
                                            rx.recharts.cartesian_grid(
                                                stroke_dasharray="3 3"
                                            ),
                                            rx.recharts.graphing_tooltip(),
                                            rx.recharts.legend(),
                                            data=ResultsState.tg_section1_round_chart_data,
                                            width=500,
                                            height=300,
                                        ),
                                        border="1px solid #E2E8F0",
                                        border_radius="lg",
                                        padding="1.5em",
                                        width="50%",
                                        margin_right="1em",
                                    ),
                                    spacing="4",
                                    width="100%",
                                    align_items="flex-start",
                                ),
                            ),
                        ),
                    ),
                    align_items="center",
                    spacing="4",
                    width="100%",
                ),
                value="tg1",
            ),
            rx.tabs.content(
                rx.vstack(  # Added vstack for consistency and centering
                    rx.heading(
                        "신뢰 게임 (수탁자 역할) 결과 분석",
                        size="6",
                        margin_top="1em",
                        margin_bottom="1em",
                    ),
                    rx.cond(
                        True,
                        # ResultsState.current_game_loaded == "trust_game",
                        rx.cond(
                            ResultsState.has_tg_section2_data_to_display,
                            rx.fragment(
                                rx.grid(
                                    # summary_card(
                                    #     "총 라운드",
                                    #     ResultsState.tg_section2_summary[
                                    #         "total_rounds"
                                    #     ],
                                    # ),
                                    summary_card(
                                        "당신이 보낸\n포인트 평균",
                                        ResultsState.tg_section2_summary[
                                            "avg_amount_sent"
                                        ],
                                        unit="포인트",
                                    ),
                                    # summary_card(
                                    #     "Total Opponent Sent",
                                    #     ResultsState.tg_section2_summary[
                                    #         "total_amount_sent"
                                    #     ],
                                    #     unit="points",
                                    # ),
                                    summary_card(
                                        "돌려받은\n포인트 평균",
                                        ResultsState.tg_section2_summary[
                                            "avg_amount_returned"
                                        ],
                                        unit="포인트",
                                        type="opponent",
                                    ),
                                    summary_card(
                                        "당신의\n평균 순이익",
                                        ResultsState.tg_section2_summary["user_payoff"],
                                        unit="포인트",
                                    ),
                                    summary_card(
                                        "상대방의\n평균 순이익",
                                        ResultsState.tg_section2_summary[
                                            "player_b_payoff"
                                        ],
                                        unit="포인트",
                                        type="opponent",
                                    ),
                                    summary_card(
                                        "당신의\n최종 잔액",
                                        ResultsState.tg_section2_summary[
                                            "user_balance"
                                        ],
                                        unit="포인트",
                                    ),
                                    summary_card(
                                        "상대방의\n최종 잔액",
                                        ResultsState.tg_section2_summary[
                                            "player_b_balance"
                                        ],
                                        unit="포인트",
                                        type="opponent",
                                    ),
                                    columns="repeat(auto-fit, minmax(150px, 1fr))",
                                    spacing="4",
                                    width="100%",
                                    max_width="1000px",
                                ),
                                rx.hstack(
                                    rx.box(
                                        rx.heading(
                                            "보낸 포인트와 돌려준 포인트",
                                            size="5",
                                            margin_bottom="1em",
                                        ),
                                        rx.recharts.line_chart(
                                            rx.recharts.line(
                                                data_key="amount_sent",
                                                name="보낸 포인트",
                                                stroke="#f43f5e",
                                                type_="monotone",
                                            ),
                                            rx.recharts.line(
                                                data_key="amount_returned",
                                                name="돌려준 포인트",
                                                stroke="#7c3aed",
                                                type_="monotone",
                                            ),
                                            rx.recharts.x_axis(
                                                data_key="stage_round",
                                                name="Stage-Round",
                                                ticks=ResultsState.tg_section2_stage_round_ticks,
                                            ),
                                            rx.recharts.y_axis(name="Points"),
                                            rx.recharts.cartesian_grid(
                                                stroke_dasharray="3 3"
                                            ),
                                            rx.recharts.graphing_tooltip(),
                                            rx.recharts.legend(),
                                            data=ResultsState.tg_section2_round_chart_data,
                                            width=500,
                                            height=300,
                                        ),
                                        border="1px solid #E2E8F0",
                                        border_radius="lg",
                                        padding="1.5em",
                                        width="50%",
                                    ),
                                    rx.box(
                                        rx.heading(
                                            "순이익",
                                            size="5",
                                            margin_bottom="1em",
                                        ),
                                        rx.recharts.line_chart(
                                            rx.recharts.line(
                                                data_key="user_payoff",
                                                name="당신의 순이익",
                                                stroke="#f43f5e",
                                                type_="monotone",
                                            ),
                                            rx.recharts.line(
                                                data_key="player_b_payoff",
                                                name="상대방 순이익",
                                                stroke="#7c3aed",
                                                type_="monotone",
                                            ),
                                            rx.recharts.x_axis(
                                                data_key="stage_round",
                                                name="Stage-Round",
                                                ticks=ResultsState.tg_section2_stage_round_ticks,
                                            ),
                                            rx.recharts.y_axis(name="Points"),
                                            rx.recharts.cartesian_grid(
                                                stroke_dasharray="3 3"
                                            ),
                                            rx.recharts.graphing_tooltip(),
                                            rx.recharts.legend(),
                                            data=ResultsState.tg_section2_round_chart_data,
                                            width=500,
                                            height=300,
                                        ),
                                        border="1px solid #E2E8F0",
                                        border_radius="lg",
                                        padding="1.5em",
                                        width="50%",
                                        margin_right="1em",
                                    ),
                                    spacing="4",
                                    width="100%",
                                    align_items="flex-start",
                                ),
                            ),
                        ),
                        rx.text(
                            "No Trust Game Section 2 data to display. Play the game to see your results."
                        ),
                    ),
                    align_items="center",
                    spacing="4",
                    width="100%",
                ),
                value="tg2",
            ),
            defaultValue="pgg",
            width="100%",
            padding_x="2em",  # Add some horizontal padding to the tabs root
        ),
        align="center",
        spacing="7",
        padding_top="2em",  # Reduced top padding for the main vstack
        width="100%",
        max_width="1200px",  # Max width for the whole page content
        margin="0 auto",  # Center the page content
    )
