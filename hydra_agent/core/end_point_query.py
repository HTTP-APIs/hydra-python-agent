from core.utils.classes_objects import RequestError
from core.utils.redis_proxy import RedisProxy
from core.utils.encode_result import encode_result


class EndPointQuery:
    """
    EndpointQuery is used for get the endpoints from the redis.

    Attributes:
        connection(RedisProxy) : An instance of redis client.
    """

    def __init__(self, graph):
        self.connection = RedisProxy().get_connection()
        self.graph = graph

    def get_allEndpoints(self, query: str):
        """
        Gets all the endpoints(classEndpoints as well as collectionEndpoints)

        Args:
            query: query gets from the user.
            graph: mainGraph stored in the redis.

        Returns:
            Data stored in redis memory
        """

        graphQueryClass = 'MATCH (p:classes) RETURN p'
        graphQueryCollections = 'MATCH (p:collection) RETURN p'

        try:
            resultClass = self.graph.redis_graph.query(graphQueryClass)
        except RequestError as err:
            raise err
        try:
            resultCollection = self.graph.redis_graph.query(graphQueryCollections)
        except RequestError as err:
            raise err

        encode_result(resultClass)
        encode_result(resultCollection)

        print("Class Endpoints -- \n")
        resultClass.pretty_print()
        print("Collection Endpoints -- \n")
        resultCollection.pretty_print()

        return str(resultClass.result_set) + str(resultCollection.result_set)

    def get_classEndpoints(self, query: str):
        """
        Gets all the classEndpoints

        Args:
            query: query gets from the user.
            graph: mainGraph stored in the redis.

        Returns:
            Data stored in redis memory
        """

        graphQueryClass = 'MATCH (p:classes) RETURN p'
        try:
            resultClass = self.graph.redis_graph.query(graphQueryClass)
        except Exception as err:
            raise err
        encode_result(resultClass)

        print("Class Endpoints -- \n")
        resultClass.pretty_print()

        return resultClass

    def get_collectionEndpoints(self, query: str):
        """
        Gets all the collectionEndpoints

        Args:
            query: query gets from the user.
            graph: mainGraph stored in the redis.

        Returns:
            Data stored in redis memory
        """

        graphQueryCollections = 'MATCH (p:collection) RETURN p'
        try:
            resultCollection = self.graph.redis_graph.query(graphQueryCollections)
        except Exception as err:
            raise err
        encode_result(resultCollection)

        print("Collection Endpoints -- \n")
        resultCollection.pretty_print()

        return resultCollection
