import reflex as rx
from ..questionnaire_state import QuestionnaireState
from typing import List
from ..components.common_styles import primary_button

# It's good practice to define styles or import them if they are common
# For this component, we'll define some basic styles inline or use Radix defaults.


def questionnaire_ui_component() -> rx.Component:
    """
    Renders a UI for the current questionnaire using data from QuestionnaireState.
    The radio button options for each item are displayed horizontally within a single table cell.
    """
    # Define some styles for the table to match the desired appearance
    table_border_style = {
        "border": "1px solid #E2E8F0",
        "padding": "0.75rem",
    }  # Light gray border, padding
    header_style = {
        **table_border_style,
        "font_weight": "600",
        "background_color": "#F9FAFB",
    }  # Bold, light gray background
    cell_style = {**table_border_style, "text_align": "center", "vertical_align": "middle"}
    item_text_cell_style = {
        **table_border_style,
        "text_align": "left",
        "vertical_align": "middle",
    }
    # The radio cell style will ensure the radio group inside is centered if it doesn't take full width.
    # However, the hstack inside will be set to 100% width.
    radio_container_cell_style = {**table_border_style, "vertical_align": "middle"}

    # Helper component to display Likert anchors horizontally in the header
    # This needs to be defined carefully to ensure it's reactive if anchors can change (though unlikely for a single questionnaire view)
    def anchors_header_comp(anchors: rx.Var[List[str]]) -> rx.Component:
        return rx.hstack(
            rx.foreach(
                anchors,  # Iterate directly over the anchors Var
                lambda anchor, idx: rx.fragment(  # Lambda receives item (anchor) and index (idx)
                    rx.cond(  # Add divider only if not the first item (index > 0)
                        idx > 0,
                        rx.divider(orientation="vertical", height="auto", margin_x="0.5em", border_color="#E2E8F0"),
                        rx.fragment(),  # No divider for the first item
                    ),
                    rx.box(
                        rx.text(
                            anchor,  # Use the anchor item directly
                            size="2",
                            weight="regular",
                            style={
                                "display": "block",
                                "text_align": "center",
                                "white_space": "pre-line",
                            },
                        ),
                        flex_grow="1",
                        text_align="center",
                        padding_x="0.25em",  # Add some padding around text to not touch divider
                    ),
                ),
            ),
            spacing="0",
            width="100%",
            justify_content="space-around",
            align_items="stretch",  # Ensure dividers and text boxes stretch vertically
        )

    return rx.vstack(
        rx.heading(QuestionnaireState.current_questionnaire, size="7", margin_bottom="1em"),
        rx.center(
            rx.vstack(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("번호", style={**header_style, "width": "7%"}),
                            rx.table.column_header_cell("문항", style={**header_style, "width": "48%"}),
                            rx.table.column_header_cell(
                                anchors_header_comp(QuestionnaireState.current_likert_anchors),
                                style={
                                    **header_style,
                                    "width": "45%",
                                    "padding_left": "0px",
                                    "padding_right": "0px",
                                },
                            ),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(
                            QuestionnaireState.current_items,
                            lambda item_text, item_idx: rx.table.row(
                                rx.table.cell(
                                    item_idx + 1,
                                    style={**cell_style, "word_break": "break-word", "white_space": "pre-line"},
                                ),
                                rx.table.cell(
                                    item_text,
                                    style={
                                        **item_text_cell_style,
                                        "word_break": "break-word",
                                        "white_space": "pre-line",
                                    },
                                ),
                                rx.table.cell(
                                    rx.radio(
                                        items=QuestionnaireState.current_likert_options_as_strings,
                                        value=rx.cond(
                                            QuestionnaireState.current_responses[item_idx].is_not_none(),
                                            QuestionnaireState.current_responses[item_idx],
                                            "",
                                        ),
                                        on_change=lambda selected_value: QuestionnaireState.set_response(
                                            item_idx,
                                            selected_value,
                                        ),
                                        direction="row",
                                        spacing="4",
                                        width="100%",
                                        justify_content="space-around",
                                        color_scheme="orange",
                                    ),
                                    style={
                                        **radio_container_cell_style,
                                        "word_break": "break-word",
                                        "white_space": "pre-line",
                                    },
                                ),
                            ),
                        )
                    ),
                    variant="surface",
                    size="2",
                    width="100%",
                    style={
                        "border_collapse": "collapse",
                        "table_layout": "fixed",
                        "max_width": "800px",
                        "word_break": "break-word",
                        "white_space": "pre-line",
                    },
                ),
                rx.spacer(height="2em"),
                primary_button(
                    "제출하기",
                    on_click=lambda: QuestionnaireState.submit_questionnaire(),
                    width="100%",
                    color_scheme="orange",
                ),
                rx.cond(
                    QuestionnaireState.error_message != "",
                    rx.callout.root(
                        rx.callout.icon(rx.icon("circle_alert")),
                        rx.callout.text(QuestionnaireState.error_message),
                        color_scheme="red",
                        variant="soft",
                        margin_top="1em",
                    ),
                ),
                align_items="stretch",
                spacing="5",
                width="100%",
                max_width="800px",
                margin="auto",
                padding="1em",
            ),
            width="100%",
        ),
        align_items="stretch",
        spacing="5",
        width="100%",
        padding="0.5em",  # Reduced padding a bit
        max_width="1000px",
        margin_x="auto",  # Center the vstack itself
    )


# Example of how this component might be used on a page:
# def my_questionnaire_page() -> rx.Component:
#     # Assume TrustGameState.user_id is already set in QuestionnaireState
#     # Or, call QuestionnaireState.set_user_id(TrustGameState.user_id) on page load/mount
#     return rx.center( # Center the component on the page
#         questionnaire_ui_component()
#     )
