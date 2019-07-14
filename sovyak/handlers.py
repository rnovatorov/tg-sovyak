import attr
import trio

from . import game as _game


@attr.s
class NewGameHandler:

    bot = attr.ib()
    games = attr.ib(factory=dict)
    command = attr.ib(default="/go")

    async def __call__(self):
        async with trio.open_nursery() as nursery:
            async with self.bot.sub(self.game_request) as updates:
                async for update in updates:
                    await nursery.start(self.new_game, update["message"]["chat"]["id"])

    async def new_game(self, chat_id, task_status=trio.TASK_STATUS_IGNORED):
        game = _game.Game(bot=self.bot, chat_id=chat_id)
        self.games[chat_id] = game
        task_status.started()
        try:
            await game()
        finally:
            del self.games[chat_id]

    def game_request(self, update):
        return (
            "message" in update
            and update["message"]["text"].startswith(self.command)
            and update["message"]["chat"]["id"] not in self.games
        )


def start_all(nursery, bot):
    nursery.start_soon(NewGameHandler(bot))
