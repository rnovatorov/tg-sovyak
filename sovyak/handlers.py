import re
import contextlib

import attr
import trio

from . import game


@attr.s
class NewGameHandler:

    RE_COMMAND = re.compile(r"go")

    bot = attr.ib()
    chats = attr.ib(factory=set)

    async def __call__(self):
        async with trio.open_nursery() as nursery:
            async with self.bot.sub(self.game_request) as us:
                async for u in us:
                    await nursery.start(self.new_game, u["message"]["chat"]["id"])

    async def new_game(self, chat, task_status=trio.TASK_STATUS_IGNORED):
        with self.chat_context(chat):
            task_status.started()
            players = await self.get_chat_members(chat)
            pack = await self.choose_pack()
            g = game.Game(bot=self.bot, players=players, pack=pack)
            await g.start()

    @contextlib.contextmanager
    def chat_context(self, chat):
        self.chats.add(chat)
        try:
            yield
        finally:
            del self.chats[chat]

    async def get_chat_members(self, chat):
        # FIXME: Hard code.
        return self.config.CHAT_MEMBERS

    async def choose_pack(self):
        # FIXME: Hard code.
        return self.config.PACK

    def game_request(self, u):
        return (
            "message" in u
            and self.RE_COMMAND.match(u["message"]["text"]) is not None
            and u["message"]["chat"]["id"] not in self.chats
        )
