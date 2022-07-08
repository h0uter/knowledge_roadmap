from enum import Enum, auto


class Behavior(Enum):
    GOTO = auto()
    EXPLORE = auto()
    VISIT = auto()
    OPEN_DOOR = auto()
    # PLAN_EXTRACTION_WO_EDGE = auto()
    # GUIDE_WP_EDGE = auto()
