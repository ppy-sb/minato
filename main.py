import uvicorn
from fastapi import FastAPI

from objects.stored import create_pool
from terms.gamemode import GameMode
from objects.score import get_best_scores, get_recent_scores, Score
from objects.user import User


app = FastAPI()


@app.on_event("startup")
async def startup_event():
    await create_pool()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/users/{user}/recent_activity")
async def get_recent_activity():
    return []


@app.get("/users/{user}")
async def get_user(user):
    return await get_user_mode(user, "unknown")


@app.get("/users/{user}/{mode}")
async def get_user_mode(user: str, mode: str):
    if mode not in GameMode.__members__:
        mode = "unknown"
    return await User.from_sql(user, GameMode[mode])


@app.get("/users/{user_id}/scores/{method}")
async def get_scores(
    user_id: int, method: str, include_fails: str = "0", mode: str = "osu", limit: int = 5, offset: int = 0
):
    if mode not in GameMode.__members__:
        mode = "osu"
    if method == "best":
        return await get_best_scores(user_id, include_fails == "1", mode, limit, offset)
    if method == "recent":
        return await get_recent_scores(user_id, include_fails == "1", mode, limit, offset)


@app.get("/scores/{mode}/{score_id}")
async def get_score(score_id: int, mode: str = "osu"):
    if mode not in GameMode.__members__:
        mode = "osu"
    return await Score.from_sql(score_id, GameMode[mode])


if __name__ == "__main__":
    uvicorn.run("main:app", port=7700, host="127.0.0.1")
