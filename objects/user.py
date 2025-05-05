from datetime import datetime
from typing import Optional

from pydantic import BaseModel

import config

from objects.stored import db_context
from terms.gamemode import GameMode


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
    total_hits: int
    replays_watched_by_others: int
    is_ranked: bool = True

    @staticmethod
    async def from_sql(user_id: int, country: str, mode: GameMode) -> "UserStatistics":
        async with db_context() as (_, cur):
            await cur.execute(f"select * from stats where id = %s and mode = %s", [user_id, int(mode)])
            row = await cur.fetchone()
            total_score = row["tscore"]
            current_level = get_level(total_score)
            level = {"current": current_level, "progress": get_level_progress(current_level, total_score)}
            grade_counts = {
                "ss": row["x_count"],
                "ssh": row["xh_count"],
                "s": row["s_count"],
                "sh": row["sh_count"],
                "a": row["a_count"],
            }
            pp = float(row["pp"])
            rank = await get_rank(user_id, country, pp, mode)
        return UserStatistics(
            level=level,
            grade_counts=grade_counts,
            rank=rank,
            pp=pp,
            global_rank=rank["global"],
            ranked_score=row["rscore"],
            hit_accuracy=row["acc"],
            play_count=row["plays"],
            play_time=row["playtime"],
            total_score=row["tscore"],
            maximum_combo=row["max_combo"],
            total_hits=row["total_hits"],
            replays_watched_by_others=row["replay_views"],
        )


class User(BaseModel):
    id: int
    username: str
    avatar_url: str
    country_code: str
    last_visit: datetime
    join_date: datetime
    statistics: UserStatistics
    playmode: str
    # previous_usernames: list[str]
    is_active: bool = True
    is_bot: bool = False
    is_deleted: bool = False
    is_online: bool = False
    is_supporter: bool = False
    pm_friends_only: bool = False
    profile_colour: str = config.user_default_profile_colour
    cover_url: str = config.user_default_cover_url
    has_supported: bool = True
    max_blocks: int = 50
    max_friends: int = 500
    playstyle: list[str] = config.user_default_playstyle
    post_count: int = 0
    profile_order: list[str] = config.user_default_profile_order
    cover: dict = {"custom_url": config.user_default_cover_url, "url": config.user_default_cover_url}

    @staticmethod
    async def from_sql(user: str, mode: GameMode) -> Optional["User"]:
        async with db_context() as (_, cur):
            if user.isdigit():
                await cur.execute(f"select * from users where id = %s or name = %s", [int(user), user])
            else:
                await cur.execute(f"select * from users where name = %s", [user])
            row = await cur.fetchone()
            if row is None:
                return None
            fav_mode = await get_favorite_mode(row["id"])
            if mode == GameMode.unknown:
                mode = fav_mode
            statistics = await UserStatistics.from_sql(int(row["id"]), row["country"], mode)
            avatar_url = config.server_avatar + str(row["id"])
            # await cur.execute(f"select username from username_history where user_id = %s order by change_date desc", [int(row['id'])])
            # name_history = []
            # for row2 in await cur.fetchall():
            # name_history.append(row2['username'])

        return User(
            id=row["id"],
            username=row["name"],
            avatar_url=avatar_url,
            playmode=fav_mode.as_vanilla_name,
            country_code=row["country"].upper(),
            statistics=statistics,
            last_visit=datetime.fromtimestamp(int(row["latest_activity"])),
            join_date=datetime.fromtimestamp(int(row["creation_time"])),
            # previous_usernames=name_history,
        )


async def get_rank(user_id: int, country: str, pp: float, mode: GameMode) -> dict[str, int]:
    async with db_context() as (_, cur):
        await cur.execute(
            "SELECT COUNT(*) AS higher_pp_players "
            "FROM stats s "
            "INNER JOIN users u USING(id) "
            "WHERE s.mode = %s "
            "AND s.pp > %s "
            "AND u.priv & 1 "
            "AND u.id != %s",
            [int(mode), pp, user_id],
        )
        global_rank = 1 + (await cur.fetchone())["higher_pp_players"]
        await cur.execute(
            "SELECT COUNT(*) AS higher_pp_players "
            "FROM stats s "
            "INNER JOIN users u USING(id) "
            "WHERE s.mode = %s "
            "AND s.pp > %s "
            "AND u.priv & 1 "
            "AND u.country = %s "
            "AND u.id != %s",
            [int(mode), pp, country, user_id],
        )
        country_rank = 1 + (await cur.fetchone())["higher_pp_players"]

    return {"global": global_rank, "country": country_rank}


def get_required_score_for_level(level: int) -> float:
    if level <= 100:
        if level >= 2:
            return 5000 / 3 * (4 * (level**3) - 3 * (level**2) - level) + 1.25 * (1.8 ** (level - 60))
        elif level <= 0 or level == 1:
            return 1.0  # Should be 0, but we get division by 0 below so set to 1
        return 0.0  # should never happen
    elif level >= 101:
        return 26931190829 + 1e11 * (level - 100)
    else:
        return 0.0  # should never happen


def get_level_progress(level: int, total_score: int) -> int:
    next_level_require = get_required_score_for_level(level + 1)
    return int(total_score / next_level_require * 100)


async def get_favorite_mode(user_id: int) -> GameMode:
    mode = GameMode.osu
    async with db_context() as (_, cur):
        await cur.execute(f"select mode from stats where id = %s order by plays desc", [user_id])
        mode = GameMode((await cur.fetchone())["mode"])

    return mode


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
