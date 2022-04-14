from fastapi import FastAPI

from terms.gamemode import GameMode
from objects.score import Score
from objects.user import User

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/users/{user}")
async def get_user(user):
    return await get_user(user, "unknown")


@app.get("/users/{user}/{mode}")
async def get_user(user: str, mode: str):
    if mode not in GameMode.__members__:
        mode = "unknown"
    return await User.from_sql(user, GameMode[mode])


@app.get("/users/{user_id}/scores/{type}")
async def get_score(user_id: int, include_fails: str = "0", mode: str = "osu", limit: int = 20, offset: int = 0):
    if mode not in GameMode.__members__:
        mode = "osu"
    return await Score.from_sql(user_id, include_fails == "1", mode, limit, offset)
