from PIL import Image

import reflex as rx

from .shared import TABS_MAP, ToolState, UploadState, tool_grid


class CropState(ToolState):
    x1: int = 0
    y1: int = 0
    x2: int = 0
    y2: int = 0
    str_x1: str = "0"
    str_y1: str = "0"
    str_x2: str = "0"
    str_y2: str = "0"
    original_w: int = 0
    original_h: int = 0

    async def post_upload(self):
        original = await self.check_original()
        self.x2, self.y2 = self.original_w, self.original_h = original.size
        self.str_x2, self.str_y2 = str(self.x2), str(self.y2)

    def set_cropper(self, value, label):
        try:
            value = int(value)
        except ValueError:
            return

        if label == "x1":
            self.x1 = value
            self.str_x1 = str(value)
        elif label == "y1":
            self.y1 = value
            self.str_y1 = str(value)
        elif label == "x2":
            self.x2 = value
            self.str_x2 = str(value)
        else:
            self.y2 = value
            self.str_y2 = str(value)

    async def trigger_crop(self):
        upload: UploadState = await self.get_state(UploadState)
        upload.result = upload.original.crop((self.x1, self.y1, self.x2, self.y2))


TABS_MAP["crop"] = CropState


def area_preview():

    scale = CropState.original_w / 300
    return rx.heading("Preview"), rx.box(
        rx.image(src=UploadState.original, width="300px"),
        rx.cond(
            CropState.has_image,
            rx.box(
                position="absolute",
                top=f"calc({CropState.y1}px / {scale})",
                left=f"calc({CropState.x1}px / {scale})",
                width=f"calc(({CropState.x2}px - {CropState.x1}px) / {scale})",
                height=f"calc(({CropState.y2}px - {CropState.y1}px) / {scale})",
                border="1px solid red",
            ),
            rx.text(CropState.has_image),
        ),
        position="relative",
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
        area_preview(),
        rx.grid(
            rx.vstack(
                _input("x1", CropState.str_x1),
                _input("y1", CropState.str_y1),
            ),
            rx.vstack(
                _input("x2", CropState.str_x2),
                _input("y2", CropState.str_y2),
            ),
            columns="2",
            width="300px",
        ),
        rx.button(
            "Crop",
            on_click=CropState.trigger_crop,
            disabled=(~CropState.x1 & ~CropState.y1 & ~CropState.x2 & ~CropState.y2),
        ),
        align="center",
    )


def crop_tool():
    return tool_grid(
        title="Crop",
        subtitle="Crop the image to a specific size",
        tool_content=cropper_form(),
        # preview_extra=area_preview(),
    )
