import asyncio
import os
from io import BytesIO
from uuid import uuid4

import requests
from aiohttp import ClientWebSocketResponse
from dotenv import load_dotenv
from mipa import Bot
from mipac.models import NotificationNote
from PIL import Image

from bg_remover import BEN2


class Misskey(Bot):
    def __init__(self) -> None:
        super().__init__()
        self.remover = BEN2()

    async def __connect_channel(self) -> None:
        await self.router.connect_channel(["main"])

    async def on_ready(self, ws: ClientWebSocketResponse) -> None:
        await self.__connect_channel()

    async def on_reconnect(self, ws: ClientWebSocketResponse) -> None:
        await self.__connect_channel()

    async def on_error(self, err):
        await self.__connect_channel()

    async def on_mention(self, notice: NotificationNote):
        uploaded_file_ids = []
        note = notice.note

        if not note.text or note.text.find("透過") == -1 or note.user.is_bot:
            return

        for file in note.files:
            res = requests.get(file.url)

            input_img = Image.open(BytesIO(res.content))
            output_img = self.remover.remove_background(input_img)

            output_bytes = BytesIO()
            output_img.save(output_bytes, format="WebP")

            uploaded_file = await self.client.drive.files.action.create(
                output_bytes.getvalue(),
                name=str(uuid4()),
                is_sensitive=file.is_sensitive,
            )
            uploaded_file_ids.append(uploaded_file.id)

        await note.api.action.reply(files=uploaded_file_ids)


async def main() -> None:
    load_dotenv()
    MISSKEY_HOST = os.getenv("MISSKEY_HOST")
    MISSKEY_TOKEN = os.getenv("MISSKEY_TOKEN")
    assert MISSKEY_HOST, "no misskey host"
    assert MISSKEY_TOKEN, "no misskey token"
    mk = Misskey()
    await mk.start(f"wss://{MISSKEY_HOST}", MISSKEY_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
