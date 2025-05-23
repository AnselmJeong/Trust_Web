import reflex as rx

# Common Styles
COLORS = {
    "primary": "#f97316",  # From Trust_Web.py (same)
    "primary_dark": "#f85a05", # From Trust_Web.py (same)
    "background": "#f3f4f6", # From Trust_Web.py (same)
    "text": "#4b5563", # From Trust_Web.py (same)
    "text_light": "#6b7280", # From Trust_Web.py (same)
    "border": "#e5e7eb", # From Trust_Web.py (same)
    "white": "#FFFAEF", # Prioritized from common_styles.py (Trust_Web.py had "white")
    "footer_bg": "#64748b", # Added for layout.py footer
    "background_light": "#f9fafb", # Added for section_1.py
    "plum": "#8E44AD", # Added for plum button
    "plum_dark": "#7D3C98", # Added for plum button hover
}

STYLES = {
    "page_container": {
        "width": "100%",
        "min_height": "100vh", # Added from Trust_Web.py
        "bg": COLORS["background"], # Changed from COLORS["white"] to COLORS["background"] based on Trust_Web.py
        "pt": "16",
    },
    "card": {
        "bg": COLORS["white"],
        "border_radius": "xl",
        "width": "100%",
        "max_width": "600px",
        "box_shadow": "0 1px 3px 0 rgb(0 0 0 / 0.1)", # Added from Trust_Web.py
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
        "bg": COLORS["white"], # Added from Trust_Web.py
        "border": f"1px solid {COLORS['border']}", # Kept from Trust_Web.py (was "1px solid #e5e7eb")
        "p": "2", # Kept from Trust_Web.py (common_styles had padding: "12px") - this uses reflex shorthand
        "border_radius": "md", # Kept from Trust_Web.py (common_styles had "6px") - this uses reflex shorthand
        "mb": "4", # Kept from Trust_Web.py (common_styles had margin_bottom: "8px") - this uses reflex shorthand
        # Properties from common_styles.py that were different or not present in Trust_Web.py's input style:
        "width": "100%", # Was already in common_styles.py
        "font_size": "18px", # Was in common_styles.py
        "min_height": "40px", # Was in common_styles.py
        # "padding": "12px", # common_styles.py version, replaced by p:"2"
        # "margin_bottom": "8px", # common_styles.py version, replaced by mb:"4"
    },
    "header_shadow": { # Added for layout.py header
        "box_shadow": "0 4px 16px 0 rgba(0,0,0,0.12)",
    },
    "button_plum": {
        "bg": COLORS["plum"],
        "color": COLORS["white"],
        "font_weight": 600,
        "font_size": "18px",
        "padding": "14px 32px",
        "border_radius": "md",
        "width": "100%",
        "_hover": {"bg": COLORS["plum_dark"]},
    },
}


def page_container(*children, **kwargs) -> rx.Component:
    """Common container for all pages."""
    container_style = STYLES["page_container"].copy()
    card_style = STYLES["card"].copy()

    content_max_width = kwargs.pop("content_max_width", None)
    if content_max_width is not None:
        card_style["max_width"] = content_max_width

    content_width = kwargs.pop("content_width", None)
    if content_width is not None:
        card_style["width"] = content_width

    padding_top = kwargs.pop("padding_top", container_style.pop("pt", "16"))
    padding_x = kwargs.pop("padding_x", None)

    container_style["pt"] = padding_top
    if padding_x is not None:
        container_style["px"] = padding_x

    return rx.box(
        rx.center(
            rx.box(
                *children,
                **card_style,
            ),
            width="100%",
        ),
        **container_style,
        **kwargs,
    )


def primary_button(text: str, **kwargs) -> rx.Component:
    """Primary button with consistent styling."""
    # Start with a copy of the default styles
    button_styles = STYLES["button"].copy()

    # If 'style' is passed in kwargs, update the defaults with it
    if "style" in kwargs:
        passed_styles = kwargs.pop("style")  # Remove 'style' from kwargs to avoid passing it as a separate prop
        button_styles.update(passed_styles)  # passed_styles will override keys in button_styles

    # Pass the merged styles as the 'style' prop, and remaining kwargs directly
    return rx.button(text, style=button_styles, size="3", **kwargs)


def section_heading(text: str, **kwargs) -> rx.Component:
    """Section heading with consistent styling."""
    # Merge default styles with any passed-in styles
    # Ensure white_space is added or overridden correctly
    style_args = STYLES["heading"].copy()
    style_args["white_space"] = "pre-line"  # Add or override white_space
    style_args.update(kwargs.pop("style", {}))  # Merge with style dict from kwargs

    # Pass other kwargs directly
    return rx.heading(text, style=style_args, **kwargs)


def plum_button(text: str, **kwargs) -> rx.Component:
    """Plum button with consistent styling."""
    # Start with a copy of the default styles
    button_styles = STYLES["button_plum"].copy()

    # If 'style' is passed in kwargs, update the defaults with it
    if "style" in kwargs:
        passed_styles = kwargs.pop("style")  # Remove 'style' from kwargs to avoid passing it as a separate prop
        button_styles.update(passed_styles)  # passed_styles will override keys in button_styles

    # Pass the merged styles as the 'style' prop, and remaining kwargs directly
    return rx.button(text, style=button_styles, size="3", **kwargs)
