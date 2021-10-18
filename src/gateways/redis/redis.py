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

    def hset(self, name: str, mapping: Dict):
        for k, v in mapping.items():
            self.redis_client.hset(name, k, v)

    def hget(self, name: str, key: str) -> str:
        return self.redis_client.hget(name, key)
