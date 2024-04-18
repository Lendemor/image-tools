from PIL import Image
import reflex as rx

from .shared import TABS_MAP, ToolState, UploadState, tool_grid


class RotateState(ToolState):
    angle: str = "0"
    expand: bool = True

    async def post_upload(self):
        await self.check_original()

    async def trigger_rotate(self):
        upload: UploadState = await self.get_state(UploadState)
        upload.result = upload.original.rotate(int(self.angle), expand=self.expand)
        self.angle = "0"


TABS_MAP["rotate"] = RotateState


def rotate_form():
    column_ratio = "40% 60%"

    def _input(label):
        return rx.grid(
            rx.center(rx.text(label)),
            rx.input(
                label=label,
                value=RotateState.angle,
                on_change=RotateState.set_angle,
            ),
            columns=column_ratio,
            width="100%",
        )

    return rx.vstack(
        _input("Angle"),
        rx.checkbox(
            "Expand",
            checked=RotateState.expand,
            on_change=RotateState.set_expand,
        ),
        rx.button(
            "Rotate",
            on_click=RotateState.trigger_rotate,
            disabled=(RotateState.angle == "0") | ~RotateState.has_image,
        ),
        align="center",
    )


def rotate_tool():
    return tool_grid(
        title="Rotate Image",
        subtitle=rx.text("Rotate an image by a specified angle."),
        tool_content=rotate_form(),
    )
