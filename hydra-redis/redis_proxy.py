"""
This is use to provide the connection to Redis memory. 
"""

import redis

class RedisProxy:
    """
    RedisProxy is used for make a connection to the Redis.
    """

    def __init__(self):
        self.connection = redis.StrictRedis(host='localhost', port=6379, db=0)

    def get_connection(self):
        return self.connection
