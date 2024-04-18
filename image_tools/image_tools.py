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


app = rx.App(theme=rx.theme(appearance="dark"), overlay_component=None)
app.add_page(index)


@rx.page(route="/styling_test", title="Styling Test", description="Test of the styling")
def index() -> rx.Component:
    return rx.container(
        rx.heading("Styling Test", size="5"),
        rx.box(
            rx.hstack(
                rx.text("This is a test of the styling"),
                rx.text("This is a test of the styling", color="green"),
            ),
            border="1px solid red",
            color="orange",
        ),
        rx.box(
            rx.hstack(
                rx.button("button 1"),
                rx.button("button 2", color="green"),
            ),
            border="1px solid yellow",
            color="orange",
        ),
    )
