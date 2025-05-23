import reflex as rx
from Trust_Web.results_state import ResultsState  # Import ResultsState
from typing import Any


def summary_card(title: str, value: rx.Var[Any], unit: str = "") -> rx.Component:
    """Helper function to create a styled summary card."""
    return rx.box(
        rx.vstack(
            rx.text(title, font_size="0.8em", color_scheme="gray"),
            rx.hstack(
                rx.heading(value, size="5"),
                rx.text(unit, font_size="1em", color_scheme="gray", margin_left="0.2em")
                if unit
                else rx.fragment(),
                align_items="baseline",
            ),
            align_items="center",  # Center text and heading inside vstack
            spacing="1",
        ),
        padding="1.5em",
        border="1px solid #E2E8F0",
        border_radius="lg",
        width="100%",  # Ensure cards take full width in their grid cell
        # bg="white", # Optional: set a background for cards
        # box_shadow="sm" # Optional: add a subtle shadow
    )


def results_page() -> rx.Component:
    """UI for the experiment results page."""
    return rx.vstack(
        rx.heading(
            "Game Score Dashboard", size="8", margin_bottom="0.2em"
        ),  # Main title like the image
        rx.text(
            "Analyze your performance across different economic games.",
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
                        "Public Goods Game - Analysis",
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
                                    summary_card(
                                        "Total Rounds",
                                        ResultsState.pgg_overall_summary[
                                            "total_rounds"
                                        ],
                                    ),
                                    summary_card(
                                        "Avg. Your Contribution",
                                        ResultsState.pgg_overall_summary[
                                            "avg_contribution"
                                        ],
                                        unit="points/round",
                                    ),
                                    summary_card(
                                        "Total Your Contribution",
                                        ResultsState.pgg_overall_summary[
                                            "total_contribution"
                                        ],
                                        unit="points",
                                    ),
                                    summary_card(
                                        "Avg. Your Payoff",
                                        ResultsState.pgg_overall_summary["avg_payoff"],
                                        unit="points/round",
                                    ),
                                    summary_card(
                                        "Total Your Payoff",
                                        ResultsState.pgg_overall_summary[
                                            "total_payoff"
                                        ],
                                        unit="points",
                                    ),
                                    columns="repeat(auto-fit, minmax(200px, 1fr))",  # Responsive grid
                                    spacing="4",
                                    width="100%",
                                    max_width="1000px",  # Limit max width of the grid
                                ),
                                # Line Chart for Payoff and Contribution over rounds
                                rx.box(
                                    rx.heading(
                                        "Performance Over Rounds",
                                        size="5",
                                        margin_top="2em",
                                        margin_bottom="1em",
                                    ),
                                    rx.recharts.line_chart(
                                        rx.recharts.line(
                                            data_key="payoff",
                                            name="Your Payoff",
                                            stroke="#8884d8",
                                            type="monotone",
                                        ),
                                        rx.recharts.line(
                                            data_key="contribution",
                                            name="Your Contribution",
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
                        "Trust Game - Section 1 Analysis",
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
                                    summary_card(
                                        "Total Rounds",
                                        ResultsState.tg_section1_summary[
                                            "total_rounds"
                                        ],
                                    ),
                                    summary_card(
                                        "Avg. Opponent Sent",
                                        ResultsState.tg_section1_summary[
                                            "avg_amount_sent"
                                        ],
                                        unit="points/round",
                                    ),
                                    summary_card(
                                        "Total Opponent Sent",
                                        ResultsState.tg_section1_summary[
                                            "total_amount_sent"
                                        ],
                                        unit="points",
                                    ),
                                    summary_card(
                                        "Avg. You Returned",
                                        ResultsState.tg_section1_summary[
                                            "avg_amount_returned"
                                        ],
                                        unit="points/round",
                                    ),
                                    summary_card(
                                        "Total You Returned",
                                        ResultsState.tg_section1_summary[
                                            "total_amount_returned"
                                        ],
                                        unit="points",
                                    ),
                                    summary_card(
                                        "Your Final Balance",
                                        ResultsState.tg_section1_summary[
                                            "player_a_balance"
                                        ],
                                        unit="points",
                                    ),
                                    summary_card(
                                        "Opponent Final Balance",
                                        ResultsState.tg_section1_summary[
                                            "user_balance"
                                        ],
                                        unit="points",
                                    ),
                                    columns="repeat(auto-fit, minmax(200px, 1fr))",
                                    spacing="4",
                                    width="100%",
                                    max_width="1000px",
                                ),
                                rx.hstack(
                                    rx.box(
                                        rx.heading(
                                            "Amounts Sent & Returned Over Rounds",
                                            size="5",
                                            margin_bottom="1em",
                                        ),
                                        rx.recharts.line_chart(
                                            rx.recharts.line(
                                                data_key="amount_sent",
                                                name="Amount Sent",
                                                stroke="#7c3aed",
                                                type_="monotone",
                                            ),
                                            rx.recharts.line(
                                                data_key="amount_returned",
                                                name="Amount Returned",
                                                stroke="#f43f5e",
                                                type_="monotone",
                                            ),
                                            rx.recharts.x_axis(
                                                data_key="round", name="Round"
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
                                                data_key="player_b_payoff",
                                                name="Your Payoff",
                                                stroke="#1976d2",
                                                type_="monotone",
                                            ),
                                            rx.recharts.line(
                                                data_key="player_a_payoff",
                                                name="Player A Payoff",
                                                stroke="#43a047",
                                                type_="monotone",
                                            ),
                                            rx.recharts.x_axis(
                                                data_key="round", name="Round"
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
                        "Trust Game - Section 2 Analysis",
                        size="6",
                        margin_top="1em",
                        margin_bottom="1em",
                    ),
                    rx.cond(
                        ResultsState.current_game_loaded == "trust_game",
                        rx.cond(
                            ResultsState.statistics,
                            rx.code_block(
                                ResultsState.formatted_statistics,
                                language="json",
                                width="100%",
                            ),
                            rx.text(
                                "No Trust Game data to display or data is loading. Click tab again or check console."
                            ),
                        ),
                        rx.text("Click one of the 'Trust Game' tabs to load data."),
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
