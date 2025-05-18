import reflex as rx
from ..questionnaire_state import QuestionnaireState
from typing import List

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
        "min_width": "300px",
        "max_width": "450px",
    }
    # The radio cell style will ensure the radio group inside is centered if it doesn't take full width.
    # However, the hstack inside will be set to 100% width.
    radio_container_cell_style = {**table_border_style, "vertical_align": "middle"}

    # Helper component to display Likert anchors horizontally in the header
    # This needs to be defined carefully to ensure it's reactive if anchors can change (though unlikely for a single questionnaire view)
    def anchors_header_comp(anchors: rx.Var[List[str]]) -> rx.Component:
        return rx.hstack(
            rx.foreach(
                anchors,
                lambda anchor: rx.box(
                    rx.text(anchor, size="2", weight="regular", align="center"),
                    # Each anchor text takes up proportional width.
                    # Ensure the parent hstack has justify_content or items are flex-grow.
                    flex_grow="1",  # Make items take available space
                    text_align="center",
                ),
            ),
            spacing="0",  # No space between anchor texts themselves, padding is on the box
            width="100%",
            justify_content="space-around",  # Distributes items evenly
        )

    return rx.vstack(
        rx.heading(QuestionnaireState.current_questionnaire, size="7", margin_bottom="1em"),
        rx.vstack(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("번호", style={**header_style, "width": "5%"}),
                        rx.table.column_header_cell("문항", style={**header_style, "width": "50%"}),
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
                            rx.table.cell(item_idx + 1, style=cell_style),
                            rx.table.cell(
                                item_text,
                                style=item_text_cell_style,
                            ),
                            rx.table.cell(
                                rx.radio(
                                    items=QuestionnaireState.current_likert_options_as_strings,
                                    value=rx.cond(
                                        QuestionnaireState.current_responses[
                                            item_idx
                                        ].is_not_none(),
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
                                ),
                                style=radio_container_cell_style,
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
                },
            ),
            rx.spacer(height="2em"),
            rx.button(
                "제출하기",
                on_click=lambda: QuestionnaireState.submit_questionnaire(),
                size="3",
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
            max_width="900px",
            margin="auto",
            padding="1em",
        ),
    )


# Example of how this component might be used on a page:
# def my_questionnaire_page() -> rx.Component:
#     # Assume TrustGameState.user_id is already set in QuestionnaireState
#     # Or, call QuestionnaireState.set_user_id(TrustGameState.user_id) on page load/mount
#     return rx.center( # Center the component on the page
#         questionnaire_ui_component()
#     )
