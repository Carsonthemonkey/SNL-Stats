import json

_cached_scenes = None

def load_scene_data():
    global _cached_scenes

    if _cached_scenes is not None:
        return _cached_scenes
    
    with open("data/scenes.json", "r", encoding="utf-8") as f:
        _cached_scenes = json.load(f)
    return _cached_scenes


if __name__ == '__main__':
    print(load_scene_data())