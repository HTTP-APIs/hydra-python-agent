from redisgraph import Graph
from core.utils.classes_objects import RequestError
from core.utils.redis_proxy import RedisProxy
from core.utils.encode_result import encode_result

class EndPointQuery:
    """
    EndpointQuery is used for get the endpoints from the Redis.

    Attributes:
        connection(RedisProxy) : An instance of redis client.
    """

    def __init__(self):
        self.connection = RedisProxy().get_connection()

    def get_allEndpoints(self, query : str, graph : Graph):
        """
        Gets all the endpoints(classEndpoints as well as collectionEndpoints)

        Args:
            query: query gets from the user.
            graph: mainGraph stored in the redis.

        Returns:
            result_set: Data stored in redis
        """

        graphQueryClass = 'MATCH (p:classes) RETURN p'
        graphQueryCollections = 'MATCH (p:collection) RETURN p'

        resultClass = graph.redis_graph.query(graphQueryClass)
        resultCollection = graph.redis_graph.query(graphQueryCollections)

        encode_result(resultClass)
        encode_result(resultCollection)

        print("Class Endpoints -- \n")
        resultClass.pretty_print()
        print("Collection Endpoints -- \n")
        resultCollection.pretty_print()

        return str(resultClass.result_set) + str(resultCollection.result_set) 

    def get_classEndpoints(self, query : str, graph : Graph):
        """
        It will return all class Endpoints.

        Args:
            query: query gets from the user.
            graph: mainGraph stored in the redis.
        
        Returns:
            result_set(str): Data stored in redis.
        """

        graphQueryClass = 'MATCH (p:classes) RETURN p'
        resultClass = graph.query(graphQueryClass)
        encode_result(resultClass)

        print("Class Endpoints -- \n")
        resultClass.pretty_print()

        return resultClass.result_set

    def get_collectionEndpoints(self, query : str, graph : Graph):
        """
        It will returns all collection Endpoints.
        
        Args:
            query: query gets from the user.
            graph: mainGraph stored in the redis.
        
        Returns:
            result_set(str): Data stored in redis.
        """

        graphQueryCollections = 'MATCH (p:collection) RETURN p'
        resultCollection = graph.query(graphQueryCollections)
        encode_result(resultCollection)

        print("Collection Endpoints-- \n")
        resultCollection.pretty_print()

        return resultCollection.result_set