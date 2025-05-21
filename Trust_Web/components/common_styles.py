import reflex as rx

# Common Styles
COLORS = {
    "primary": "#f97316",
    "primary_dark": "#f85a05",
    "background": "#f3f4f6",
    "text": "#4b5563",
    "text_light": "#6b7280",
    "border": "#e5e7eb",
    "white": "#FFFAEF",
}

STYLES = {
    "page_container": {
        "width": "100%",
        "bg": COLORS["white"],
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
        "width": "80%",
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
    return rx.button(text, style=button_styles, **kwargs)


def section_heading(text: str, **kwargs) -> rx.Component:
    """Section heading with consistent styling."""
    # Merge default styles with any passed-in styles
    # Ensure white_space is added or overridden correctly
    style_args = STYLES["heading"].copy()
    style_args["white_space"] = "pre-line"  # Add or override white_space
    style_args.update(kwargs.pop("style", {}))  # Merge with style dict from kwargs

    # Pass other kwargs directly
    return rx.heading(text, style=style_args, **kwargs)
