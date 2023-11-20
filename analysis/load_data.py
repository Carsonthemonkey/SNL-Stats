import json
from schema import Sketch

_cached_scenes = None
_cached_videos = None
_cached_full_data = None

def load_scene_data():
    global _cached_scenes

    if _cached_scenes is not None:
        return _cached_scenes
    
    with open("data/scenes.json", "r", encoding="utf-8") as f:
        _cached_scenes = json.load(f)
    return _cached_scenes


def load_video_data():
    global _cached_videos

    if _cached_videos is not None:
        return _cached_videos
    
    with open("data/channel_videos.json", "r", encoding="utf-8") as f:
        _cached_videos = json.load(f)
    return _cached_videos

def load_full_data():
    global _cached_full_data
    if _cached_full_data is not None:
        return _cached_full_data
    with open("data/full_data.json", "r", encoding="utf-8") as f:
        _cached_full_data = json.load(f)
    _cached_full_data = [Sketch(**sketch) for sketch in _cached_full_data["full_data"]]
    return _cached_full_data

if __name__ == '__main__':
    print(load_scene_data())