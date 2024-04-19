from io import BytesIO

from PIL import Image

import reflex as rx

TABS_MAP = {}


class ToolState(rx.State):
    has_image: bool = False

    async def check_original(self):
        upload: UploadState = await self.get_state(UploadState)
        self.has_image = bool(upload.original)
        return upload.original


class TabState(rx.State):
    active_tab: str = "crop"

    async def set_active_tab(self, value: str):
        self.active_tab = value
        active = await self.get_state(TABS_MAP[self.active_tab])
        await active.post_upload(refresh=False)

    async def get_active_state(self):
        return TABS_MAP[self.active_tab]


class UploadState(rx.State):
    original: Image.Image = None
    result: Image.Image = None
    uploading: bool = False
    upload_progress: int = 0
    active_tool: str = "resize"

    async def handle_upload(self, files: list[rx.UploadFile]):
        self.original = Image.open(BytesIO(await files[0].read()))
        self.uploading = False
        yield
        tabs = await self.get_state(TabState)
        yield (await tabs.get_active_state()).post_upload

    async def swap_result(self):
        self.original = self.result
        self.result = None
        tabs = await self.get_state(TabState)
        yield (await tabs.get_active_state()).post_upload

    async def handle_upload_progress(self, progress: dict):
        self.uploading, self.upload_progress = True, round(progress["progress"] * 100)

    def cancel_upload(self):
        self.uploading, self.upload_progress = False, 0
        return rx.cancel_upload("upload")


def original_preview():
    def upload_button():
        return rx.upload(
            rx.button(rx.icon("upload"), "Upload Image"),
            id="upload",
            on_drop=UploadState.handle_upload(
                rx.upload_files(
                    upload_id="upload",
                    on_upload_progress=UploadState.handle_upload_progress,
                )
            ),
        )

    def progress_bar():
        return rx.hstack(
            rx.progress(value=UploadState.upload_progress, max=100, width="300px"),
            rx.icon_button(
                "X", on_click=UploadState.cancel_upload, color_scheme="crimson"
            ),
            align="center",
        )

    return rx.vstack(
        rx.heading("Original"),
        rx.spacer(),
        rx.cond(
            UploadState.original,
            rx.image(src=UploadState.original, width="300px"),
            rx.center(
                rx.cond(
                    UploadState.uploading, progress_bar(), rx.text("No image uploaded")
                ),
            ),
        ),
        rx.spacer(),
        upload_button(),
        align="center",
        min_height="50vh",
    )


def result_image():
    return rx.vstack(
        rx.heading("Result"),
        rx.spacer(),
        rx.image(src=UploadState.result, width="300px"),
        rx.spacer(),
        rx.cond(
            UploadState.result,
            rx.button("Use this result as source.", on_click=UploadState.swap_result),
        ),
        align="center",
    )


def grid_item(*content):
    return rx.box(
        *content,
        align="center",
        background=rx.color("gray", 4),
        border_radius="10px",
        padding="1em",
    )


def tool_grid(title, subtitle, tool_content, preview_extra=None):
    res_img = result_image()

    return rx.container(
        rx.vstack(
            rx.heading(title, size="7"),
            subtitle,
            rx.grid(
                grid_item(original_preview()),
                grid_item(rx.center(tool_content, height="100%")),
                grid_item(preview_extra) if preview_extra else rx.fragment(),
                grid_item(res_img),
                columns="4" if preview_extra else "3",
                spacing="4",
            ),
            align="center",
        ),
        size="4",
    )
