from PIL import Image

import reflex as rx

from .shared import TABS_MAP, ToolState, UploadState, tool_grid


class FlipState(ToolState):
    horizontal: bool = False
    vertical: bool = False

    async def post_upload(self, refresh=True):
        await self.check_original()

    async def trigger_flip(self):
        upload: UploadState = await self.get_state(UploadState)
        image = upload.original
        if self.horizontal:
            image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        if self.vertical:
            image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        upload.result = image

    def set_checkbox(self, value, label):
        if label == "Horizontal":
            self.horizontal = value
        else:
            self.vertical = value


TABS_MAP["flip"] = FlipState


def flipper_form():
    def _checkbox(label, var):
        return rx.checkbox(
            label,
            checked=var,
            on_change=lambda value: FlipState.set_checkbox(value, label),
        )

    return rx.vstack(
        _checkbox("Horizontal", FlipState.horizontal),
        _checkbox("Vertical", FlipState.vertical),
        rx.button(
            "Flip",
            on_click=FlipState.trigger_flip,
            disabled=~(
                FlipState.has_image & (FlipState.horizontal | FlipState.vertical)
            ),
        ),
    )


def flip_tool():
    return tool_grid(
        title="Flip",
        subtitle="Flip the image horizontally or vertically.",
        tool_content=flipper_form(),
    )
