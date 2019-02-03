from core.utils.redis_proxy import RedisProxy
from core.utils.handle_data import HandleData
from core.utils.encode_result import encode_result


class PropertiesQuery:
    """
    PropertiesQuery is used to query properties of various types:
    classes or collection endpoints, members, object etc.
    """

    def __init__(self):
        self.connection = RedisProxy.get_connection()
        self._data = HandleData()

    def get_classes_properties(self, query, graph):
        """
        Show the given type of property of given Class endpoint.

        Args:
            query: Input query from the user

        Returns:
            Data from the Redis memory.
        """
        query = query.replace("class", "")
        endpoint, query = query.split(" ")
        graphQuery = 'MATCH ( p:classes ) WHERE (p.type="{}") RETURN p.{}'.format(
            endpoint, query)

        try:
            resultData = graph.redis_graph.query(graphQuery)
        except Exception as err:
            raise err
        encode_result(resultData)

        print("class", endpoint, query)
        resultData.pretty_print()

        return resultData.result_set

    def get_collection_properties(self, query, graph):
        """
        Query properties of collection based on input

        Args:
            query: Input query from the user

        Returns:
            Data from the Redis memory.
        """
        endpoint, query = query.split(" ")

        graphQuery = 'MATCH ( p:collection ) WHERE (p.type="{}") RETURN p.{}'.format(
            endpoint, query)

        try:
            resultData = graph.redis_graph.query(graphQuery)
        except Exception as err:
            raise err
        encode_result(resultData)

        print("collection", endpoint, query)
        resultData.pretty_print()

        return resultData.result_set

    def get_members_properties(self, query, graph):
        """
        Query properties of member based on input

        Args:
            query: Input query from the user

        Returns:
            Data from the Redis memory.
        """
        endpoint, query = query.split(" ")

        graphQuery = "MATCH ( p:{} ) RETURN p.id,p.{}".format(endpoint, query)

        try:
            resultData = graph.redis_graph.query(graphQuery)
        except Exception as err:
            raise err
        encode_result(resultData)

        print("member", endpoint, query)
        resultData.pretty_print()

        return resultData.result_set

    def get_object_property(self, query, graph):
        """
        Show the given type of property of given object.

        Args:
            query: Input query from the user

        Returns:
            Data from the Redis memory.
        """
        endpoint, query = query.split(" ")
        endpoint = endpoint.replace("object", "")
        index = endpoint.find("Collection")
        id_ = "object" + endpoint[5:index]

        graphQuery = 'MATCH (p:{}) WHERE (p.parent_id = "{}") RETURN p.{}'.format(
            id_, endpoint, query)

        try:
            resultData = graph.redis_graph.query(graphQuery)
        except Exception as err:
            raise err
        encode_result(resultData)

        print("object", endpoint, query)
        resultData.pretty_print()

        return resultData.result_set
