import attr


@attr.s
class Players:

    _players = attr.ib()

    def __iter__(self):
        return iter(list(self.players.values()))

    def __enter__(self):
        for player in self._players.values():
            player.can_answer = True
            player.reviewee = None

    def __exit__(self, *exc):
        assert self.are_done

    @property
    def are_done(self):
        for player in self._players.values():
            assert not player.can_answer
            assert player.reviewee is None

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

    @classmethod
    def from_id_list(cls, ids):
        players = {id: Player(id for id in ids)}
        return cls(players)


Ers = Players


@attr.s
class Player:

    id = attr.ib()
    score = attr.ib(default=0)
    can_answer = attr.ib(default=True)
    reviewee = attr.ib(default=None)
