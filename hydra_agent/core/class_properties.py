from core.utils.redis_proxy import RedisProxy
from core.utils.encode_result import encode_result
from core.utils.classes_objects import ClassEndpoints
from hydra_python_core.doc_maker import HydraDoc
from redisgraph.query_result import QueryResult


class ClassPropertiesValue:
    """
    Used to fetch properties of classEndpoints and store them in redis

    Attributes:
        url: URL of the API Documentation
        api_doc: HydraDoc object of the API Documentation
        connection: Instance of redis-client
        class_nodes: Dictionary of classEndpoints
    """

    def __init__(self, api_doc: HydraDoc, url: str, graph):
        self.url = url
        self.api_doc = api_doc
        self.connection = RedisProxy.get_connection()
        self.class_nodes = ClassEndpoints(
            graph.redis_graph, graph.class_endpoints, self.api_doc)

    def data_from_server(self, endpoint: str) -> QueryResult:
        """
        Loads data from the server

        Args:
            endpoint: Concerned classEndpoint

        Returns:
            Data from the redis memory
        """
        self.class_nodes.load_from_server(
            endpoint, self.api_doc, self.url, self.connection)

        graphQuery = """MATCH (p:classes) WHERE(p.type='{}')
                        RETURN p.property_value""".format(endpoint)

        try:
            resultData = self.graph.redis_graph.query(graphQuery)
        except Exception as err:
            raise err
        encode_result(resultData)

        print("{} property_value".format(endpoint))
        # resultData.pretty_print()

        return resultData

    def get_property_value(self, query: str) -> QueryResult:
        """
        Loads data from the server.
        Keeps about existing data in redis memory

        Args:
            query: Input query from the user.

        Returns:
            Data from the redis memory.
        """
        query = query.replace("class", "")
        endpoint = query.replace(" property_value", "")
        if str.encode("fs:endpoints") in self.connection.keys() and str.encode(
            endpoint
        ) in self.connection.smembers("fs:endpoints"):
            graphQuery = """MATCH (p:classes) WHERE (p.type = '{}')
                            RETURN p.property_value""".format(endpoint)
            try:
                resultData = self.graph.redis_graph.query(graphQuery)
            except Exception as err:
                raise err
            encode_result(resultData)
        else:
            self.connection.sadd("fs:endpoints", endpoint)
            # print(self.connection.smembers("fs:endpoints"))
            resultData = self.data_from_server(endpoint)

        print(endpoint, "property_value")
        resultData.pretty_print()

        return resultData
