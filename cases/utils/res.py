from datetime import datetime

class Result:

    mid: int = None
    rid: int = None
    is_active: bool = False
    init_time: datetime = None

    def __init__(self, mid: int) -> None:
        self.mid = mid

    def set_result(self, rid: int, is_active: bool, now: datetime) -> None:
        self.is_active = is_active
        self.init_time = now
        self.rid = rid
    
    def off(self) -> None:
        self.is_active = False


# Singleton
results: dict[int, Result] = dict()