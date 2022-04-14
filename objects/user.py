from datetime import datetime
from typing import Optional

from pydantic import BaseModel

import config
from objects import stored
from terms.gamemode import GameMode

db_cursor = stored.db_cursor


class UserStatistics(BaseModel):
    level: dict[str, int]
    grade_counts: dict[str, int]
    rank: dict[str, int]
    pp: float
    global_rank: int
    ranked_score: int
    hit_accuracy: float
    play_count: int
    play_time: int
    total_score: int
    maximum_combo: int
    total_hits = 0
    replays_watched_by_others = 0
    is_ranked = True

    @staticmethod
    async def from_sql(user_id: int, country: str, mode: GameMode) -> 'UserStatistics':
        db_cursor.execute(f"select * from stats where id = %s and mode = %s", [user_id, int(mode)])
        rows = db_cursor.fetchone()
        total_score = rows['tscore']
        current_level = get_level(total_score)
        level = {"current": current_level,
                 "progress": get_level_progress(current_level, total_score)}
        grade_counts = {"ss": rows['x_count'], "ssh": rows['xh_count'], "s": rows['s_count'],
                        "sh": rows['sh_count'], "a": rows['a_count']}
        pp = float(rows['pp'])
        rank = await get_rank(user_id, country, pp, mode)
        return UserStatistics(level=level, grade_counts=grade_counts, rank=rank,
                              pp=pp, global_rank=rank['global'], ranked_score=rows['rscore'],
                              hit_accuracy=rows['acc'], play_count=rows['plays'],
                              play_time=rows['playtime'], total_score=rows['tscore'],
                              maximum_combo=rows['max_combo'])


class User(BaseModel):
    id: int
    username: str
    avatar_url: str
    country_code: str
    last_visit: datetime
    join_date: datetime
    statistics: UserStatistics
    playmode: str
    is_active = True
    is_bot = False
    is_deleted = False
    is_online = False
    is_supporter = False
    pm_friends_only = False
    profile_colour = config.user_default_profile_colour
    cover_url = config.user_default_cover_url
    has_supported = True
    max_blocks = 50
    max_friends = 500
    playstyle = config.user_default_playstyle
    post_count = 0
    profile_order = config.user_default_profile_order
    cover = {"custom_url": config.user_default_cover_url, "url": config.user_default_cover_url}

    @staticmethod
    async def from_sql(user: str, mode: GameMode) -> Optional['User']:
        if user.isdigit():
            db_cursor.execute(f"select * from users where id = %s or name = %s", [int(user), user])
        else:
            db_cursor.execute(f"select * from users where name = %s", [user])
        rows = db_cursor.fetchone()
        if rows is None:
            return None
        fav_mode = get_favorite_mode(rows['id'])
        if mode == GameMode.unknown:
            mode = fav_mode
        statistics = await UserStatistics.from_sql(int(rows['id']), rows['country'], mode)
        avatar_url = config.server_avatar + f"/{rows['id']}"
        return User(id=rows['id'], username=rows['name'], avatar_url=avatar_url, playmode=fav_mode.as_vanilla_name,
                    country_code=rows['country'].upper(), statistics=statistics,
                    last_visit=datetime.fromtimestamp(int(rows['latest_activity'])),
                    join_date=datetime.fromtimestamp(int(rows['creation_time'])))


async def get_rank(user_id: int, country: str, pp: float, mode: GameMode) -> dict[str, int]:
    db_cursor.execute(
        'SELECT COUNT(*) AS higher_pp_players '
        'FROM stats s '
        'INNER JOIN users u USING(id) '
        'WHERE s.mode = %s '
        'AND s.pp > %s '
        'AND u.priv & 1 '
        'AND u.id != %s',
        [int(mode), pp, user_id]
    )
    global_rank = 1 + db_cursor.fetchone()['higher_pp_players']
    db_cursor.execute(
        'SELECT COUNT(*) AS higher_pp_players '
        'FROM stats s '
        'INNER JOIN users u USING(id) '
        'WHERE s.mode = %s '
        'AND s.pp > %s '
        'AND u.priv & 1 '
        'AND u.country = %s '
        'AND u.id != %s',
        [int(mode), pp, country, user_id]
    )
    country_rank = 1 + db_cursor.fetchone()['higher_pp_players']
    return {"global": global_rank, "country": country_rank}


def get_required_score_for_level(level: int) -> float:
    if level <= 100:
        if level >= 2:
            return 5000 / 3 * (4 * (level ** 3) - 3 * (level ** 2) - level) + 1.25 * (1.8 ** (level - 60))
        elif level <= 0 or level == 1:
            return 1.0  # Should be 0, but we get division by 0 below so set to 1
    elif level >= 101:
        return 26931190829 + 1e11 * (level - 100)


def get_level_progress(level: int, total_score: int) -> int:
    next_level_require = get_required_score_for_level(level + 1)
    return int(total_score / next_level_require * 100)


def get_favorite_mode(user_id: int) -> GameMode:
    db_cursor.execute(f"select mode from stats where id = %s order by plays desc", [user_id])
    return GameMode(db_cursor.fetchone()['mode'])


def get_level(total_score: int) -> int:
    level = 1
    while True:
        # Avoid endless loops
        if level > 120:
            return level

        # Calculate required score
        req_score = get_required_score_for_level(level)

        # Check if this is our level
        if total_score <= req_score:
            # Our level, return it and break
            return level - 1
        else:
            # Not our level, calculate score for next level
            level += 1
