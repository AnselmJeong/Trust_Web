import reflex as rx
# from Trust_Web.trust_game_state import TrustGameState # Unused
# from Trust_Web.questionnaire_state import QuestionnaireState # Unused
from Trust_Web.authentication import AuthState
from Trust_Web.components import (
    login_form,
    instructions_page,
    public_goods_game_component,
    section_1,
    section_2,
    stage_transition,
    final_page,
    questionnaire_ui_component,
    demography_form,
    landing_page,
    results_page,
)
from Trust_Web.layout import layout
# from Trust_Web.components.common_styles import STYLES, COLORS, page_container, primary_button, section_heading # Removed import


# Page component mapping dictionary
PAGE_COMPONENT_MAPPING = {
    # "demography": rx.center(demography_form(), width="100%"),
    # "questionnaire": rx.center(questionnaire_ui_component(), width="100%"),
    "demography": demography_form(),
    "questionnaire": questionnaire_ui_component(),
    "public-goods": public_goods_game_component(),
    "section1": section_1(),
    "section2": section_2(),
    "stage-transition": stage_transition(),
    "final": final_page(),
    "results": results_page(),
}

# The main app content with layout
@rx.page(route="/app/[page_id]", on_load=AuthState.on_load_app_page_check)
def app_page():
    """Dynamic app page that shows different content based on page_id."""
    current_page_id = AuthState.router.page.params.get("page_id", "")  # Use .get for safety

    print(
        f"[APP_PAGE] Loading. Page ID: {current_page_id}, User Auth: {AuthState.is_authenticated}, User ID: {AuthState.user_id}"
    )

    # Create a list of (value, component) tuples for rx.match
    match_cases = [(page_name, component_func) for page_name, component_func in PAGE_COMPONENT_MAPPING.items()]

    content = rx.match(
        current_page_id,
        *match_cases,  # Unpack the list of tuples
        rx.heading(rx.text(f"Unknown page: {current_page_id}"), size="4"),  # Default case
    )

    return rx.fragment(
        layout(content),
    )


# Root page for landing and login modal
@rx.page(route="/", on_load=AuthState.on_load_index_page_check)
def index():
    """Root page that shows the landing page and login modal if needed."""
    print(f"[INDEX_PAGE] Loading. User Auth: {AuthState.is_authenticated}")
    # The main content of the landing page
    landing_content = rx.fragment(
        landing_page(),
        # The login modal is kept here as it's specific to the landing page context
        # when a user is not authenticated and tries to access functionality.
        # The layout already handles a global login modal if initiated from the nav header.
        # However, this placement ensures it appears correctly if triggered on the landing page itself.
        # rx.cond(
        #     AuthState.show_login_modal,
        #     rx.dialog.root(
        #         rx.dialog.content(
        #             rx.dialog.close(
        #                 rx.icon(
        #                     tag="x",
        #                     style={
        #                         "cursor": "pointer",
        #                         "position": "absolute",
        #                         "top": "0.8rem",
        #                         "right": "0.8rem",
        #                         "color": "#AAAAAA",
        #                         "_hover": {"color": "#333333"},
        #                     },
        #                     on_click=AuthState.close_login_modal,
        #                 )
        #             ),
        #             login_form(),
        #             style={
        #                 "padding": "2em",
        #                 "borderRadius": "1em",
        #                 "minWidth": "350px",
        #                 "maxWidth": "350px",
        #                 "position": "relative",
        #                 "bg": "#fefaef",
        #             },
        #         ),
        #         open=AuthState.show_login_modal,
        #         on_open_change=AuthState.set_login_modal_state,
        #     ),
        # ),
    )
    return layout(landing_content)


# Create the app
app = rx.App(
    theme=rx.theme(
        color_mode="light",
        initial_color_mode="light",
        use_system_color_mode=False,
    )
)
