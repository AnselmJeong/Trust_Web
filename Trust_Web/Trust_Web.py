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


# The login page (shown when not authenticated)
def login_page() -> rx.Component:
    """Login page without layout."""
    return login_form()


# The main app content with layout
@rx.page(route="/app/[page_id]", on_load=AuthState.on_load_app_page_check)
def app_page():
    """Dynamic app page that shows different content based on page_id."""
    page_id = AuthState.router.page.params.page_id

    # Logging for app_page
    print(
        f"[APP_PAGE] Loading. User Auth: {AuthState.is_authenticated}, User ID: {AuthState.user_id}"
    )

    # auth_check = rx.cond(  # We will rely on on_load for this
    #     ~TrustGameState.is_authenticated | (TrustGameState.user_id == ""),
    #     rx.script("window.location.href = '/'"),
    #     None,
    # )

    # Map page_id to the appropriate component
    content = rx.cond(
        page_id == "questionnaire",
        rx.center(questionnaire_ui_component(), width="100%"),
        rx.cond(
            page_id == "instructions",
            instructions(),
            rx.cond(
                page_id == "public-goods",
                public_goods_game_component(),
                rx.cond(
                    page_id == "section1",
                    section_1(),
                    rx.cond(
                        page_id == "section-transition",
                        section_transition(),
                        rx.cond(
                            page_id == "section2",
                            section_2(),
                            rx.cond(
                                page_id == "stage-transition",
                                stage_transition(),
                                rx.cond(
                                    page_id == "final",
                                    final_page(),
                                    rx.heading(f"Unknown page: {page_id}", size="4"),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )

    # Apply the layout to the content
    return rx.fragment(
        # auth_check, # Removed as on_load should handle this
        layout(content),
    )


# Root page for login and redirection
@rx.page(route="/", on_load=AuthState.on_load_index_page_check)
def index():
    """Root page that shows login or redirects to app if authenticated."""
    # Logging for index page
    print(f"[INDEX_PAGE] Loading. User Auth: {AuthState.is_authenticated}")

    # redirect_if_authenticated = rx.cond( # We will rely on on_load for this
    #     TrustGameState.is_authenticated,
    #     rx.script("window.location.href = '/app/questionnaire'"),
    #     None,
    # )

    return rx.fragment(
        # redirect_if_authenticated, # Removed as on_load should handle this
        login_page(),
    )


# Create the app
app = rx.App()
