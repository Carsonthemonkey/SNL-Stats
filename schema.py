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

class Sketch(BaseModel):
    id: str
    title: str
    scene_type: str
    cast: List[str]
    upload_date: Optional[str] = None
    duration: Optional[str] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    mean_sentiment: Optional[float] = None
    std_sentiment: Optional[float] = None