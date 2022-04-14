# -*- coding: utf-8 -*-

import functools
from enum import IntFlag, unique


@unique
class Mods(IntFlag):
    NOMOD = 0
    NOFAIL = 1 << 0
    EASY = 1 << 1
    TOUCHSCREEN = 1 << 2
    HIDDEN = 1 << 3
    HARDROCK = 1 << 4
    SUDDENDEATH = 1 << 5
    DOUBLETIME = 1 << 6
    RELAX = 1 << 7
    HALFTIME = 1 << 8
    NIGHTCORE = 1 << 9
    FLASHLIGHT = 1 << 10
    AUTOPLAY = 1 << 11
    SPUNOUT = 1 << 12
    AUTOPILOT = 1 << 13
    PERFECT = 1 << 14
    KEY4 = 1 << 15
    KEY5 = 1 << 16
    KEY6 = 1 << 17
    KEY7 = 1 << 18
    KEY8 = 1 << 19
    FADEIN = 1 << 20
    RANDOM = 1 << 21
    CINEMA = 1 << 22
    TARGET = 1 << 23
    KEY9 = 1 << 24
    KEYCOOP = 1 << 25
    KEY1 = 1 << 26
    KEY3 = 1 << 27
    KEY2 = 1 << 28
    SCOREV2 = 1 << 29
    MIRROR = 1 << 30

    def as_list(self) -> list[str]:
        result = []
        for mod in Mods:
            if self.value & mod:
                result.append(mod_dict[mod])
        return result


mod_dict = {
    Mods.NOFAIL: 'NF',
    Mods.EASY: 'EZ',
    Mods.TOUCHSCREEN: 'TD',
    Mods.HIDDEN: 'HD',
    Mods.HARDROCK: 'HR',
    Mods.SUDDENDEATH: 'SD',
    Mods.DOUBLETIME: 'DT',
    Mods.RELAX: 'RX',
    Mods.HALFTIME: 'HT',
    Mods.NIGHTCORE: 'NC',
    Mods.FLASHLIGHT: 'FL',
    Mods.AUTOPLAY: 'AU',
    Mods.SPUNOUT: 'SO',
    Mods.AUTOPILOT: 'AP',
    Mods.PERFECT: 'PF',
    Mods.FADEIN: 'FI',
    Mods.RANDOM: 'RN',
    Mods.CINEMA: 'CN',
    Mods.TARGET: 'TP',
    Mods.SCOREV2: 'V2',
    Mods.MIRROR: 'MR',

    Mods.KEY1: '1K',
    Mods.KEY2: '2K',
    Mods.KEY3: '3K',
    Mods.KEY4: '4K',
    Mods.KEY5: '5K',
    Mods.KEY6: '6K',
    Mods.KEY7: '7K',
    Mods.KEY8: '8K',
    Mods.KEY9: '9K',
    Mods.KEYCOOP: 'CO'
}
