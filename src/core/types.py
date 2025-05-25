from enum import Enum


class SwipeAction(str, Enum):
    LIKE = "like"
    DISLIKE = "dislike"
    HIDE = "hide"
