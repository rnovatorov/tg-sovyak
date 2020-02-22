import attr
import trio


@attr.s
class Players:

    _players = attr.ib()
    _mutex = attr.ib(factory=trio.Lock)

    def __iter__(self):
        return iter(list(self._players.values()))

    def __contains__(self, id):
        return id in self._players

    async def are_done(self):
        async with self._mutex:
            for player in self._players.values():
                if player.can_answer or player.reviewee is not None:
                    return False
            return True

    def reset_state(self):
        for player in self._players.values():
            player.can_answer = True
            player.reviewee = None

    def by_id(self, id):
        return self._players[id]

    def choose_reviewer(self, answer):
        for player in self._players.values():
            if (
                not player.can_answer
                and player.reviewee is None
                and player is not answer.sender
            ):
                return player
        return None

    async def prohibit_answers(self):
        async with self._mutex:
            for player in self._players.values():
                player.can_answer = False

    @classmethod
    def from_id_list(cls, ids):
        players = {id: Player(id) for id in ids}
        return cls(players)


Ers = Players


@attr.s
class Player:

    id = attr.ib()
    score = attr.ib(default=0)
    can_answer = attr.ib(default=True)
    reviewee = attr.ib(default=None)
