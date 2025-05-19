import reflex as rx
from Trust_Web.trust_game_state import TrustGameState
from Trust_Web.questionnaire_state import QuestionnaireState
from Trust_Web.authentication import AuthState
from Trust_Web.components import (
    login_form,
    instructions,
    public_goods_game_component,
    section_1,
    section_2,
    section_transition,
    stage_transition,
    final_page,
    questionnaire_ui_component,
    demography_form,
    landing_page,
)
from Trust_Web.layout import layout

# Common Styles
COLORS = {
    "primary": "#f97316",
    "primary_dark": "#f85a05",
    "background": "#f3f4f6",
    "text": "#4b5563",
    "text_light": "#6b7280",
    "border": "#e5e7eb",
    "white": "white",
}

STYLES = {
    "page_container": {
        "width": "100%",
        "min_height": "100vh",
        "bg": COLORS["background"],
        "pt": "16",
    },
    "card": {
        "bg": COLORS["white"],
        "border_radius": "xl",
        "width": "100%",
        "max_width": "600px",
        "box_shadow": "0 1px 3px 0 rgb(0 0 0 / 0.1)",
        "padding": "8",
    },
    "heading": {
        "font_weight": 600,
        "size": "6",
        "mb": "6",
    },
    "button": {
        "bg": COLORS["primary"],
        "color": COLORS["white"],
        "font_weight": 600,
        "font_size": "18px",
        "padding": "14px 32px",
        "border_radius": "md",
        "width": "100%",
        "_hover": {"bg": COLORS["primary_dark"]},
    },
    "input": {
        "bg": COLORS["white"],
        "border": f"1px solid {COLORS['border']}",
        "p": "2",
        "border_radius": "md",
        "mb": "4",
    },
}


# Page component mapping dictionary
PAGE_COMPONENT_MAPPING = {
    "demography": rx.center(demography_form(), width="100%"),
    "questionnaire": rx.center(questionnaire_ui_component(), width="100%"),
    "instructions": instructions(),
    "public-goods": public_goods_game_component(),
    "section1": section_1(),
    "section-transition": section_transition(),
    "section2": section_2(),
    "stage-transition": stage_transition(),
    "final": final_page(),
}


def page_container(*children, **kwargs) -> rx.Component:
    """Common container for all pages."""
    container_style = STYLES["page_container"].copy()
    card_style = STYLES["card"].copy()

    padding_top = kwargs.pop("padding_top", container_style.pop("pt", "16"))
    padding_x = kwargs.pop("padding_x", None)

    container_style["pt"] = padding_top
    if padding_x:
        container_style["px"] = padding_x

    return rx.box(
        rx.center(
            rx.box(
                *children,
                **card_style,
            ),
        ),
        **container_style,
        **kwargs,
    )


def primary_button(text: str, **kwargs) -> rx.Component:
    """Primary button with consistent styling."""
    return rx.button(text, **STYLES["button"], **kwargs)


def section_heading(text: str, **kwargs) -> rx.Component:
    """Section heading with consistent styling."""
    return rx.heading(text, **STYLES["heading"], **kwargs)


# The main app content with layout
@rx.page(route="/app/[page_id]", on_load=AuthState.on_load_app_page_check)
def app_page():
    """Dynamic app page that shows different content based on page_id."""
    current_page_id = AuthState.router.page.params.get("page_id", "") # Use .get for safety

    print(
        f"[APP_PAGE] Loading. Page ID: {current_page_id}, User Auth: {AuthState.is_authenticated}, User ID: {AuthState.user_id}"
    )

    # Create a list of (value, component) tuples for rx.match
    match_cases = [
        (page_name, component_func) 
        for page_name, component_func in PAGE_COMPONENT_MAPPING.items()
    ]
    
    content = rx.match(
        current_page_id, 
        *match_cases, # Unpack the list of tuples
        rx.heading(rx.text(f"Unknown page: {current_page_id}"), size="4") # Default case
    )

    return rx.fragment(
        layout(content),
    )


# Root page for landing and login modal
@rx.page(route="/", on_load=AuthState.on_load_index_page_check)
def index():
    """Root page that shows the landing page and login modal if needed."""
    print(f"[INDEX_PAGE] Loading. User Auth: {AuthState.is_authenticated}")
    return rx.fragment(
        landing_page(),
        rx.cond(
            AuthState.show_login_modal,
            rx.dialog.root(
                rx.dialog.overlay(),
                rx.dialog.content(
                    login_form(),
                    rx.dialog.close(
                        rx.button("닫기", on_click=AuthState.close_login_modal, style={"marginTop": "1em"})
                    ),
                    style={"padding": "2em", "borderRadius": "1em", "minWidth": "350px"},
                ),
                open=AuthState.show_login_modal,
                on_open_change=lambda open: AuthState.close_login_modal() if not open else None,
            ),
        ),
    )


# Create the app
app = rx.App()
