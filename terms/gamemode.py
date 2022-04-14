import functools
from enum import IntEnum


class GameMode(IntEnum):
    unknown = -1
    osu = 0
    taiko = 1
    fruits = 2
    mania = 3

    osuRx = 4
    taikoRx = 5
    fruitsRx = 6

    osuAp = 7

    @functools.cached_property
    def scores_table(self) -> str:
        if self.value < self.osuRx:
            return 'scores_vn'
        elif self.value < self.osuAp:
            return 'scores_rx'
        else:
            return 'scores_ap'

    @functools.cached_property
    def as_vanilla(self) -> int:
        if self.value == self.osuAp:
            return 0

        return self.value % 4

    @functools.cached_property
    def as_vanilla_name(self) -> str:
        return GameMode(self.as_vanilla).name
