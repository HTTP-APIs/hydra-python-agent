"""
This is use to provide the connection to Redis memory.
"""

import redis
import os

class RedisProxy:
    """
    RedisProxy is used for make a connection to the Redis.
    """

    def __init__(self):
        host = os.getenv("REDIS_HOST", "localhost")
        self.connection = redis.StrictRedis(host=host, port=6379, db=0)

    def get_connection(self):
        return self.connection
