from redisgraph import Graph
from redisgraph.query_result import QueryResult
from core.utils.redis_proxy import RedisProxy
from core.utils.encode_result import encode_result


class PropertiesQuery:
    """
    PropertiesQuery is used to query properties of various types:
    classes or collection endpoints, members, object etc.

    Attributes:
        connection: Instance of redis-client
        graph: Instance of InitializeGraph for the API Documentation
    """

    def __init__(self, graph: Graph):
        self.connection = RedisProxy.get_connection()
        self.graph = graph

    def get_classes_properties(self, query: str) -> QueryResult:
        """
        Gets properties of a classEndpoint based on input

        Args:
            query: Input query from the user

        Returns:
            Data from the redis memory.
        """
        query = query.replace("class", "")
        endpoint, query = query.split(" ")
        graphQuery = 'MATCH ( p:classes ) WHERE (p.type="{}") RETURN p.{}'.format(
            endpoint, query)

        try:
            resultData = self.graph.redis_graph.query(graphQuery)
        except Exception as err:
            raise err
        encode_result(resultData)

        print("class", endpoint, query)
        resultData.pretty_print()

        return resultData

    def get_collection_properties(self, query: str) -> QueryResult:
        """
        Gets properties of a collectionEndpoint based on input

        Args:
            query: Input query from the user

        Returns:
            Data from the redis memory.
        """
        endpoint, query = query.split(" ")

        graphQuery = 'MATCH ( p:collection ) WHERE (p.type="{}") RETURN p.{}'.format(
            endpoint, query)

        try:
            resultData = self.graph.redis_graph.query(graphQuery)
        except Exception as err:
            raise err
        encode_result(resultData)

        print("collection", endpoint, query)
        resultData.pretty_print()

        return resultData

    def get_members_properties(self, query: str) -> QueryResult:
        """
        Gets members of collectionEndpoint based on input

        Args:
            query: Input query from the user

        Returns:
            Data from the redis memory.
        """
        endpoint, query = query.split(" ")

        graphQuery = "MATCH ( p:{} ) RETURN p.id,p.{}".format(endpoint, query)

        try:
            resultData = self.graph.redis_graph.query(graphQuery)
        except Exception as err:
            raise err
        encode_result(resultData)

        print("member", endpoint, query)
        resultData.pretty_print()

        return resultData

    def get_object_property(self, query: str) -> QueryResult:
        """
        Gets properties of objects

        Args:
            query: Input query from the user

        Returns:
            Data from the redis memory.
        """
        endpoint, query = query.split(" ")
        endpoint = endpoint.replace("object", "")
        index = endpoint.find("Collection")
        id_ = "object" + endpoint[5:index]

        graphQuery = 'MATCH (p:{}) WHERE (p.parent_id = "{}") RETURN p.{}'.format(
            id_, endpoint, query)

        try:
            resultData = self.graph.redis_graph.query(graphQuery)
        except Exception as err:
            raise err
        encode_result(resultData)

        print("object", endpoint, query)
        resultData.pretty_print()

        return resultData
