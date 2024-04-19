from PIL import Image

import reflex as rx

from .shared import TABS_MAP, ToolState, UploadState, tool_grid


class CropState(ToolState):
    crop_x: int = 0
    crop_y: int = 0
    crop_width: int = 0
    crop_height: int = 0
    original_w: int = 0
    original_h: int = 0

    async def post_upload(self, refresh=True):
        original = await self.check_original()
        if refresh and self.has_image:
            self.crop_x, self.crop_y = 0, 0
            self.crop_width, self.crop_height = self.original_w, self.original_h = (
                original.size
            )

    @rx.var
    def x2(self) -> int:
        return self.crop_x + self.crop_width

    @rx.var
    def y2(self) -> int:
        return self.crop_y + self.crop_height

    @rx.var
    def str_crop_x(self) -> str:
        return str(self.crop_x)

    @rx.var
    def str_crop_y(self) -> str:
        return str(self.crop_y)

    @rx.var
    def str_crop_width(self) -> str:
        return str(self.crop_width)

    @rx.var
    def str_crop_height(self) -> str:
        return str(self.crop_height)

    def set_cropper(self, value, label):
        try:
            value = int(value)
        except ValueError:
            return

        if label == "x":
            self.crop_x = value
            if self.crop_x + self.crop_width > self.original_w:
                self.crop_width = self.original_w - self.crop_x
        elif label == "y":
            self.crop_y = value
            if self.crop_y + self.crop_height > self.original_h:
                self.crop_height = self.original_h - self.crop_y
        elif label == "Width":
            self.crop_width = value
        else:
            self.crop_height = value

    async def trigger_crop(self):
        upload: UploadState = await self.get_state(UploadState)
        upload.result = upload.original.crop(
            (
                self.crop_x,
                self.crop_y,
                self.crop_x + self.crop_width,
                self.crop_y + self.crop_height,
            )
        )


TABS_MAP["crop"] = CropState


def area_preview():
    scale = CropState.original_w / 300
    return (
        rx.heading("Preview"),
        rx.spacer(),
        rx.box(
            rx.image(src=UploadState.original, width="300px"),
            rx.cond(
                CropState.has_image,
                rx.box(
                    position="absolute",
                    top=f"calc({CropState.crop_y}px / {scale})",
                    left=f"calc({CropState.crop_x}px / {scale})",
                    width=f"calc({CropState.crop_width}px / {scale})",
                    height=f"calc({CropState.crop_height}px / {scale})",
                    border="1px solid red",
                ),
                rx.text(CropState.has_image),
            ),
            position="relative",
            width="auto",
        ),
    )


def cropper_form():
    def _input(label, value):
        return rx.grid(
            rx.center(rx.text(label)),
            rx.input(
                label=label,
                value=value,
                on_change=lambda value: CropState.set_cropper(value, label),
            ),
            columns="40% 60%",
            width="100%",
        )

    return rx.vstack(
        *area_preview(),
        rx.grid(
            rx.vstack(
                _input("x", CropState.str_crop_x),
                _input("y", CropState.str_crop_y),
            ),
            rx.vstack(
                _input("Width", CropState.str_crop_width),
                _input("Height", CropState.str_crop_height),
            ),
            columns="2",
            width="300px",
        ),
        rx.button(
            "Crop",
            on_click=CropState.trigger_crop,
            disabled=(
                ~CropState.crop_x
                & ~CropState.crop_y
                & ~CropState.crop_width
                & ~CropState.crop_height
            ),
        ),
        align="center",
        height="100%",
    )


def crop_tool():
    return tool_grid(
        title="Crop",
        subtitle="Crop the image to a specific size",
        tool_content=cropper_form(),
    )
