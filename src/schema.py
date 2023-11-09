from pydantic import BaseModel
from typing import List
from typing import Optional

class Video(BaseModel):
    video_id: str
    title: str
    duration: str
    view_count: int
    like_count: int
    comment_count: int

class Scene(BaseModel):
    title: Optional[str] = None
    scene_type: str
    cast: List[str]

