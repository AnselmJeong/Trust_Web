import reflex as rx
from typing import Optional, List, Any # Added List, Any for children
from .common_styles import STYLES, COLORS # Assuming these might be used for card styling

def GameSectionCard(
    title: str,
    icon_name: str,
    progress_value: rx.Var[int], # type: ignore
    progress_max: int,
    header_extras: Optional[rx.Component] = None,
    *children: rx.Component, # For content
    **props: Any # For additional card props
) -> rx.Component:
    """
    A reusable card component for game sections, including a header with icon, title,
    optional extra header elements, a progress bar, and content children.
    """
    # Default card styling, can be overridden by props
    card_style = {
        "width": "clamp(300px, 80%, 600px)",
        "margin_x": "auto",
        "padding": "6", # Corresponds to p_x=6, p_y=6 -> 1.5rem if 1 unit = 0.25rem
        **STYLES.get("card", {}) # Apply common card styles, allowing overrides
    }
    # Merge with any props passed to the card, allowing further customization
    # For example, if 'width' is in props, it will override card_style["width"]
    final_card_style = {**card_style, **props.pop("style", {})}


    return rx.card(
        rx.vstack(
            # Header: Icon, Title, header_extras
            rx.hstack(
                rx.icon(tag=icon_name, mr="2"), # Use margin right for spacing
                rx.heading(title, size="7"), # Default size, can be adjusted
                rx.spacer(),
                header_extras if header_extras else rx.fragment(),
                justify_content="between", # Ensures elements are spaced out
                align_items="center",    # Vertically align items in the hstack
                width="100%",
                mb="3", # Margin bottom for spacing before progress bar
            ),
            rx.progress(
                value=progress_value,
                max=progress_max,
                width="100%",
                color_scheme="orange", # Default color, can be made a prop
                height="sm",          # Standard height
                border_radius="md",   # Rounded corners for progress bar
                mb="4", # Margin bottom for spacing before content
            ),
            # Content passed as children
            *children,
            spacing="4", # Spacing between elements in the vstack
            align_items="stretch", # Stretches children to fill width if appropriate
            width="100%", # Ensure vstack takes full width of card content area
        ),
        style=final_card_style, # Apply combined styles
        **props # Pass any other Card component props
    )
