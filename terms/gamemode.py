import functools
from enum import IntEnum


class GameMode(IntEnum):
    unknown = -1
    osu = 0
    taiko = 1
    fruits = 2
    mania = 3

    osuRX = 4
    taikoRX = 5
    fruitsRX = 6

    osuAP = 8

    @functools.cached_property
    def scores_table(self) -> str:
        if self.value < self.osuRX:
            return 'scores_vn'
        elif self.value < self.osuAP:
            return 'scores_rx'
        else:
            return 'scores_ap'

    @functools.cached_property
    def as_vanilla(self) -> int:
        if self.value == self.osuAP:
            return 0

        return self.value % 4

    @functools.cached_property
    def as_vanilla_name(self) -> str:
        return GameMode(self.as_vanilla).name

