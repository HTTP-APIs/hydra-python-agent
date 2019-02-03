from core.utils.redis_proxy import RedisProxy
from core.utils.collections_endpoint import CollectionEndpoints
from core.utils.encode_result import encode_result


class CollectionMembersQuery:
    """
    CollectionMembersQuery is used for fetching members of any
    CollectionEndpoints.
    It fetches data from the server and adds it to the redis graph.

    Attributes:
        connection(RedisProxy): An instance of redis client.


    """

    def __init__(self, api_doc, url, graph):
        self.connection = RedisProxy.get_connection()
        self.api_doc = api_doc
        self.url = url
        self.collection = CollectionEndpoints(
            graph.redis_graph, graph.class_endpoints, api_doc)

    def data_from_server(self, endpoint, graph):
        """
        Load data from the server for first time.

        Args:
            endpoint: collectionEndpoint to load members from.

        Returns:
            Get data from the Redis memory.
        """
        self.collection.load_from_server(
            endpoint, self.api_doc, self.url, self.connection
        )

        graphQuery = 'MATCH (p:collection) WHERE(p.type="{}") RETURN p.members'.format(
            endpoint
        )
        resultData = graph.redis_graph.query(graphQuery)
        encode_result(resultData)

        print("Collection {} Members -- \n".format(endpoint))
        resultData.pretty_print()

        return resultData.result_set

    def get_members(self, query, graph):
        """
        Gets Data from the Redis.

        Args:
            query: Input query from the user

        Returns:
            Data from the Redis memory.
        """
        endpoint = query.replace(" members", "")
        if str.encode("fs:endpoints") in self.connection.keys() and str.encode(
            endpoint
        ) in self.connection.smembers("fs:endpoints"):

            graphQuery = 'MATCH (p:collection) WHERE(p.type="{}") RETURN p.members'.format(
                endpoint)
            resultData = graph.redis_graph.query(graphQuery)
            encode_result(resultData)

            print(endpoint, " members ->")
            resultData.pretty_print()

            return resultData.result_set
        else:
            try:
                self.connection.sadd("fs:endpoints", endpoint)
            except Exception as err:
                raise err
            print(self.connection.smembers("fs:endpoints"))
            return self.data_from_server(endpoint)
