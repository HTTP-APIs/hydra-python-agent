from core.utils.redis_proxy import RedisProxy


def check_url_exist(check_url: str, facades):
    """
    Checks whether URL already exists in Redis or not.

    Args:
        check_url: The URL to be checked
        facades: Instance of `QueryFacades` used for initializing the graph.
    """

    connection = RedisProxy.get_connection()
    url = check_url.decode("utf-8")
    if str.encode("fs:url") in connection.keys() and check_url in connection.smembers(
        "fs:url"
    ):
        print("URL already exist in Redis")
        facades.initialize(False)
    else:
        facades.initialize(True)
        connection.sadd("fs:url", url)
