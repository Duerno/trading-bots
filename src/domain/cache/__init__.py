from typing import Dict


class Cache:
    """
    Cache defines the interface for any cache system, such as Redis.
    """

    def __init__(self, config: Dict):
        pass

    def hset(self, name: str, mapping: Dict):
        pass

    def hget(self, name: str, key: str) -> str:
        pass
