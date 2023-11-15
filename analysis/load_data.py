import json

_cached_scenes = None
_cached_videos = None

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
    
    with open("data/video_ids.json", "r", encoding="utf-8") as f:
        _cached_videos = json.load(f)
    return _cached_videos


if __name__ == '__main__':
    print(load_scene_data())