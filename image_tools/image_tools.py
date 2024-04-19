"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from .tools import crop_tool, flip_tool, resize_tool, rotate_tool
from .tools.shared import TabState


def tools_trigger(value):
    return rx.tabs.trigger(
        value.capitalize(),
        value=value,
        font_size="1.6em",
    )


TOOLS_MAP = {
    "resize": resize_tool,
    "rotate": rotate_tool,
    "flip": flip_tool,
    "crop": crop_tool,
}

color_button_style = {
    "position": "fixed",
    "right": "2em",
    "top": "2em",
    "background": "transparent",
    "color": rx.color("gray", 12),
}


def toggle_color_button():
    return rx.color_mode.button(rx.color_mode.icon(), style=color_button_style)


def tools():
    return rx.tabs.root(
        rx.tabs.list(*[tools_trigger(tool_name) for tool_name in TOOLS_MAP]),
        *[
            rx.tabs.content(tool(), value=tool_name)
            for tool_name, tool in TOOLS_MAP.items()
            if tool is not None
        ],
        value=TabState.active_tab,
        on_change=TabState.set_active_tab,
        width="100vw",
        min_height="80vh",
    )


def index() -> rx.Component:
    return rx.center(
        toggle_color_button(),
        rx.vstack(
            rx.heading("Image Tools", size="8"),
            rx.text(
                "A collection of tools for editing images. No image is stored on the server, everything is done in memory."
            ),
            tools(),
            rx.logo(),
            align="center",
        ),
        width="100vw",
        min_height="100vh",
    )


app = rx.App(
    theme=rx.theme(appearance="dark", accent_color="jade"), overlay_component=None
)
app.add_page(index)
