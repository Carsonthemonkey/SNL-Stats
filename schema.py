from pydantic import BaseModel

class Video(BaseModel):
    video_id: str
    title: str
    duration: str
    view_count: int
    like_count: int
    comment_count: int
