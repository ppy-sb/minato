from pydantic import BaseModel


class Score(BaseModel):

    @staticmethod
    async def from_sql(user_id: int, include_fails: bool, mode: str, limit: int, offset: int) -> 'Score':
        return Score()
