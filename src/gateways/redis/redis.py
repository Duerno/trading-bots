from typing import Dict

import redis
import logging

from src.domain.cache import Cache


class Redis(Cache):
    def __init__(self, config):
        self.redis_client = redis.Redis(
            host=config['redis']['host'],
            port=config['redis']['port']
        )
        self.hget('a', 'a')

    def hset(self, name: str, mapping: Dict):
        self.redis_client.hset(name, mapping)

    def hget(self, name: str, key: str) -> str:
        return self.redis_client.hget(name, key)
