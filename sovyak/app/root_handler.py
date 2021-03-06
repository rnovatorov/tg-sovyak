import re
import contextlib

import attr
import trio

from sovyak import gameplay


@attr.s
class RootHandler:

    RE_COMMAND = re.compile(r"go")

    bot = attr.ib()
    config = attr.ib()
    chats = attr.ib(factory=set)

    async def run(self):
        async with trio.open_nursery() as nursery:
            async with self.bot.sub(self.game_request) as updates:
                async for update in updates:
                    chat = update["message"]["chat"]["id"]
                    await nursery.start(self.new_game, chat)

    __call__ = run

    async def new_game(self, chat, task_status=trio.TASK_STATUS_IGNORED):
        with self.chat_context(chat):
            task_status.started()
            game = await gameplay.new_game(self.bot, self.config, chat)
            await game.run()

    @contextlib.contextmanager
    def chat_context(self, chat):
        self.chats.add(chat)
        try:
            yield
        finally:
            self.chats.remove(chat)

    def game_request(self, u):
        return (
            "message" in u
            and "text" in u["message"]
            and self.RE_COMMAND.match(u["message"]["text"]) is not None
            and u["message"]["chat"]["id"] not in self.chats
        )
