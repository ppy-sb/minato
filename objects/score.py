from datetime import datetime

from pydantic import BaseModel

import config

from objects.stored import db_context
from objects.user import User
from terms.gamemode import GameMode
from terms.mods import Mods


class Score(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    replay = True
    accuracy: float
    best_id: int
    created_at: datetime
    id: int
    max_combo: int
    mode: str
    mode_int: int
    mods: list[str]
    passed: bool
    perfect: bool
    pp: float
    rank: str
    user: User
    score: int
    statistics: dict[str, int]
    beatmap: dict[str, str]
    beatmapset: dict[str, object]
    user_id: int
    weight: dict[str, float] = []

    @staticmethod
    async def from_sql(score_id: int, mode: GameMode):
        async with db_context() as (_, cur):
            await cur.execute(f"select * from scores where id = %s and mode=%s", [score_id, mode.value])
            row = await cur.fetchone()
            if row is None:
                return {"detail": "Not Found"}
            user = await User.from_sql(str(row['userid']), mode)
            await cur.execute(f"select * from maps where md5 = %s", [row['map_md5']])
            map_row = await cur.fetchone()

        set_id = map_row['set_id']
        statistics = {
            "count_100": row['n100'],
            "count_300": row['n300'],
            "count_50": row['n50'],
            "count_geki": row['ngeki'],
            "count_katu": row['nkatu'],
            "count_miss": row['nmiss']
        }
        beatmap = {
            "beatmapset_id": map_row['set_id'],
            "id": map_row['id'],
            "version": map_row['version']
        }
        beatmapset = {
            "artist": map_row['artist'],
            "artist_unicode": map_row['artist'],
            "title": map_row['title'],
            "title_unicode": map_row['title'],
            "creator": map_row['creator'],
            "covers": {
                "cover": f"{config.beatmap_assets}{set_id}/covers/cover.jpg",
                "cover@2x": f"{config.beatmap_assets}{set_id}/covers/cover@2x.jpg",
                "card": f"{config.beatmap_assets}{set_id}/covers/card.jpg",
                "card@2x": f"{config.beatmap_assets}{set_id}/covers/card@2x.jpg",
                "list": f"{config.beatmap_assets}{set_id}/covers/list.jpg",
                "list@2x": f"{config.beatmap_assets}{set_id}/covers/list@2x.jpg",
                "slimcover": f"{config.beatmap_assets}{set_id}/covers/slimcover.jpg",
                "slimcover@2x": f"{config.beatmap_assets}{set_id}/covers/slimcover@2x.jpg"
            }
        }
        return Score(accuracy=float(row['acc']) / 100, best_id=row['id'], id=row['id'], created_at=row['play_time'],
                     max_combo=row['max_combo'], mode=mode.name, mode_int=mode.as_vanilla,
                     mods=Mods(row['mods']).as_list(), passed=(row['grade'] != "F"),
                     perfect=bool(row['perfect']), pp=row['pp'], rank=row['grade'].replace("X", "SS"),
                     score=row['score'], statistics=statistics, user_id=row['userid'], beatmap=beatmap,
                     beatmapset=beatmapset, user=user)


async def get_best_scores(user_id: int, include_fails: bool, mode: str, limit: int, offset: int):
    game_mode = GameMode[mode]
    result = []
    async with db_context() as (_, cur):
        await cur.execute(
            f'SELECT s.id, s.acc, s.pp FROM scores s '
            'INNER JOIN maps m ON s.map_md5 = m.md5 '
            'WHERE s.userid = %s AND s.mode = %s '
            'AND s.status = 2 AND m.status = 2 '
            'ORDER BY s.pp DESC '
            f'limit {offset}, {limit}',
            [user_id, game_mode.value]
        )

        for i, row in enumerate(await cur.fetchall()):
            percentage = 0.95 ** (offset + i)
            pp = row['pp'] * percentage
            score = await Score.from_sql(row['id'], game_mode)
            score.weight = {
                "percentage": percentage,
                "pp": pp
            }
            result.append(score)

    return result


async def get_recent_scores(user_id: int, include_fails: bool, mode: str, limit: int, offset: int):
    game_mode = GameMode[mode]
    result = []
    async with db_context() as (_, cur):
        await cur.execute(f'select id from scores where userid = %s and mode = %s '
                          'order by play_time desc '
                          f'limit {offset}, {limit}',
                          [user_id, game_mode.value])

        for row in await cur.fetchall():
            score = await Score.from_sql(row['id'], game_mode)
            result.append(score)
    return result
