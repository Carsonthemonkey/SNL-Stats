import json
from schema import Sketch
import datetime

_cached_scenes = None
_cached_videos = None
_cached_full_data = None


def load_scene_data():
    global _cached_scenes

    if _cached_scenes is not None:
        return _cached_scenes
    
    with open("data/scenes.json", "r", encoding="utf-8") as f:
        _cached_scenes = json.load(f)
    _cached_scenes = _cached_scenes["scene_data"]
    return _cached_scenes


def load_video_data():
    global _cached_videos

    if _cached_videos is not None:
        return _cached_videos
    
    with open("data/channel_videos.json", "r", encoding="utf-8") as f:
        _cached_videos = json.load(f)
    return _cached_videos["channel_videos"]


def is_not_recent(date: str, days: int) -> bool:
    date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
    now = datetime.datetime.now()
    return (now - date).days > days

def load_full_data():
    global _cached_full_data
    if _cached_full_data is not None:
        return _cached_full_data
    with open("data/full_data.json", "r", encoding="utf-8") as f:
        _cached_full_data = json.load(f)
    
    _cached_full_data = [Sketch(**sketch) for sketch in _cached_full_data["full_data"] if is_not_recent(sketch["upload_date"], 1000)]
    return _cached_full_data
if __name__ == '__main__':
    print(load_scene_data())