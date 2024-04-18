"""A page for resizing images."""

import reflex as rx

from .shared import TABS_MAP, ToolState, UploadState, tool_grid


class ResizeState(ToolState):
    og_width: int = 0
    og_height: int = 0
    og_ratio: float = 0
    new_width: str = ""
    new_height: str = ""
    maintain_ratio: bool = True

    @rx.var
    def rounded_ratio(self) -> str:
        return round(self.og_ratio, 2)

    async def post_upload(self):
        original = await self.check_original()
        self.og_width, self.og_height = original.size
        self.og_ratio = self.og_width / self.og_height

    def update_new_size(self, value, label):
        try:
            int(value)
        except ValueError:
            return

        if label == "Width":
            self.new_width = value
        else:
            self.new_height = value

        if self.maintain_ratio:
            if label == "Width":
                self.new_height = str(round(int(value) / self.og_ratio))
            else:
                self.new_width = str(round(int(value) * self.og_ratio))

    @rx.var
    def disable_resize(self) -> bool:
        width, height = int(self.new_width) if self.new_width else 0, (
            int(self.new_height) if self.new_height else 0
        )
        return not (self.has_image and width and height)

    async def trigger_resize(self):
        upload: UploadState = await self.get_state(UploadState)
        new_size = (int(self.new_width), int(self.new_height))

        upload.result = upload.original.resize(new_size)
        self.new_width, self.new_height = "", ""


TABS_MAP["resize"] = ResizeState


def resize_form():
    column_ratio = "40% 60%"

    def _input_disabled(label, value):
        return rx.grid(
            rx.center(rx.text(label)),
            rx.input(
                size="1",
                disabled=True,
                value=value,
                justify="end",
            ),
            columns=column_ratio,
            width="100%",
        )

    def _input(label, value):
        return rx.grid(
            rx.center(rx.text(label)),
            rx.input(
                value=value,
                on_change=lambda value: ResizeState.update_new_size(value, label),
                size="1",
                disabled=rx.cond(UploadState.original, False, True),
                justify="end",
            ),
            columns=column_ratio,
            width="100%",
        )

    return rx.vstack(
        rx.text.strong("Original"),
        _input_disabled("Width", ResizeState.og_width),
        _input_disabled("Height", ResizeState.og_height),
        _input_disabled("Ratio", ResizeState.rounded_ratio),
        rx.icon("arrow_down", color="gray"),
        rx.text.strong("New"),
        _input("Width", ResizeState.new_width),
        _input("Height", ResizeState.new_height),
        rx.hstack(
            rx.checkbox(
                "Maintain Aspect Ratio",
                checked=ResizeState.maintain_ratio,
                on_change=ResizeState.set_maintain_ratio,
            ),
        ),
        rx.button(
            "Resize",
            on_click=ResizeState.trigger_resize,
            disabled=ResizeState.disable_resize,
        ),
        align="center",
    )


def resize_tool():
    """A page for resizing images."""
    return tool_grid(
        title="Resize Image",
        subtitle=rx.text("Upload an image to resize it."),
        tool_content=resize_form(),
    )
