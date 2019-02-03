"""
This is use to provide the connection to Redis memory.
"""

import redis
import os


class RedisProxy:
    """
    RedisProxy is used for make a connection to the Redis.
    """
    @staticmethod
    def get_connection():
        """
        Connects to redis server

        Returns:
            An instance of redis client
        """
        host = os.getenv("REDIS_HOST", "localhost")
        try:
            connection = redis.StrictRedis(host=host, port=6379, db=0)
            return connection
        except ConnectionError as err:
            return "Error : {}".format(err)