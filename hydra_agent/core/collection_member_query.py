from core.utils.redis_proxy import RedisProxy
from core.utils.collections_endpoint import CollectionEndpoints
from core.utils.encode_result import encode_result
from hydra_python_core.doc_writer import HydraDoc
from redisgraph.query_result import QueryResult


class CollectionMembersQuery:
    """
    CollectionMembersQuery is used for fetching members of any
    CollectionEndpoints.
    It fetches data from the server and adds it to the redis graph.

    Attributes:
        connection: An instance of redis client.
        api_doc: HydraDoc object of the API Documentation
        url: URL of the concerned API Documentation
        graph: Instance of InitializeGraph
        collection: Instance of CollectionEndpoints.
        Used to store data in redis memory from the server
    """

    def __init__(self, api_doc: HydraDoc, url: str, graph):
        self.connection = RedisProxy.get_connection()
        self.api_doc = api_doc
        self.url = url
        self.graph = graph
        self.collection = CollectionEndpoints(
            self.graph.redis_graph, self.graph.class_endpoints, self.api_doc)

    def data_from_server(self, endpoint: str) -> QueryResult:
        """
        Load data from the server for first time.

        Args:
            endpoint: collectionEndpoint to load members from.

        Returns:
            Get data from the redis memory.
        """
        self.collection.load_from_server(
            endpoint, self.api_doc, self.url, self.connection
        )

        graphQuery = 'MATCH (p:collection) WHERE(p.type="{}") RETURN p.members'.format(
            endpoint
        )
        resultData = self.graph.redis_graph.query(graphQuery)
        encode_result(resultData)

        print("Collection {} Members -- \n".format(endpoint))
        # resultData.pretty_print()

        return resultData

    def get_members(self, query: str) -> QueryResult:
        """
        Gets Data from the redis.

        Args:
            query: Input query from the user

        Returns:
            Data from the redis memory.
        """
        endpoint = query.replace(" members", "")

        if str.encode("fs:endpoints") in self.connection.keys() and str.encode(
            endpoint
        ) in self.connection.smembers("fs:endpoints"):

            graphQuery = 'MATCH (p:collection) WHERE(p.type="{}") RETURN p.members'.format(
                endpoint)
            resultData = self.graph.redis_graph.query(graphQuery)
            encode_result(resultData)
            print(endpoint, " members ->")

        else:
            try:
                self.connection.sadd("fs:endpoints", endpoint)
            except Exception as err:
                raise err
            print(self.connection.smembers("fs:endpoints"))
            resultData = self.data_from_server(endpoint)
        resultData.pretty_print()
        return resultData
