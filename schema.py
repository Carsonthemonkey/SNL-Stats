from pydantic import BaseModel

class Video(BaseModel):
    video_id: str
    title: str
    duration: str
    view_count: int
    like_count: int
    comment_count: int


# Example validation
def main():
    v = {
        "video_id": "whee",
        "title": "hello",
        "duration": 6,
        "view_count": 6,
        "like_count": 6,
        "comment_count": 6
    }
    v = Video(**v)
    print(type(v))
    
if __name__ == "__main__":
    main()
