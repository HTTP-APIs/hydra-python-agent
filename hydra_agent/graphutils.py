from redisgraph import Node, Edge, Graph


class GraphUtils:

    def __init__(self, redis_proxy, graph_name='apidoc'):
        self.redis_proxy = redis_proxy
        self.redis_connection = redis_proxy.get_connection()
        self.graph_name = graph_name
        self.redis_graph = Graph("apidoc", redis_proxy)

    def read(self, match, ret, where=None):
        """
        Run query to read nodes in Redis and return the result
        :param match: Relationship between queried entities.
        :param ret: Defines which property/ies will be returned.
        :param where: Used to filter results, not mandatory.
        :return: Corresponding Nodes
        """
        query = "MATCH(p:{})".format(match)
        if where is not None:
            query += " WHERE(p.{})".format(where)
        query += " RETURN p.{}".format(ret)

        return self.redis_connection.execute_command("GRAPH.QUERY",
                                                     self.graph_name,
                                                     query)

    def update(self, match, set, where=None):
        """
        Run query to read nodes in Redis and return the result
        :param match: Relationship between queried entities.
        :param ret: Defines which property/ies will be returned.
        :param set: The property to be updated.
        :return: Corresponding Nodes
        """
        query = "MATCH(p:{})".format(match)
        if where is not None:
            query += " WHERE(p.{})".format(where)
        query += " SET p.{}".format(set)

        return self.redis_connection.execute_command("GRAPH.QUERY",
                                                     self.graph_name,
                                                     query)

    def addNode(self, label1, alias1, properties1):
        """
        Add node to the redis graph
        :param label1: label for the node.
        :param alias1: alias for the node.
        :param properties: properties for the node.
        :return: Created Node
        """
        node = Node(label=label1, alias=alias1, properties=properties1)
        self.redis_graph.add_node(node)
        return node

    def addEdge(self, source_node, predicate, dest_node):
        """Add edge between nodes in redis graph
        :param source_node: source node of the edge.
        :param predicate: relationship between the source and destination node
        :param dest_node: destination node of the edge.
        """
        edge = Edge(source_node, predicate, dest_node)
        self.redis_graph.add_edge(edge)

    def processOutput(self, get_data):
        """
        Partial data processing for redis-sets
        Count is using for avoid stuffs like query internal execution time.
        :param get_data: data get from the Redis memory.
        """
        count = 0
        all_property_lists = []
        for objects in get_data:
            count += 1
            # Show data only for odd value of count.
            # because for even value it contains stuffs like time and etc.
            # ex: Redis provide data like if we query class endpoint
            # output like:
            # [[endpoints in byte object form],[query execution time:0.5ms]]
            # So with the help of count, byte object convert to string
            # and also show only useful strings not the query execution time.
            if count % 2 != 0:
                for obj1 in objects:
                    for obj in obj1:
                        string = obj.decode('utf-8')
                        map_string = map(str.strip, string.split(','))
                        property_list = list(map_string)
                        check = property_list.pop()
                        property_list.append(check.replace("\x00", ""))
                        if property_list[0] != "NULL":
    #                        print(property_list)
                            all_property_lists.append(property_list)
        return all_property_lists