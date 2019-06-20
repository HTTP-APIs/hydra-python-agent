from redisgraph import Node, Edge, Graph
from typing import Union, Optional
from redis.exceptions import ResponseError


class GraphUtils:

    def __init__(self, redis_proxy, graph_name='apidoc'):
        self.redis_proxy = redis_proxy
        self.redis_connection = redis_proxy.get_connection()
        self.graph_name = graph_name
        self.redis_graph = Graph("apidoc", redis_proxy)

    def read(self, match: str, ret: str,
             where: Optional[str]=None) -> Union[int, list, ResponseError]:
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

    def update(self, match: str, set: str, where: Optional[str]=None) -> list:
        """
        Run query to update nodes in Redis and return the result
        :param match: Relationship between queried entities.
        :param set: The property to be updated.
        :param where: Used to filter results, not mandatory.
        :return: Query results
        """
        query = "MATCH(p:{})".format(match)
        if where is not None:
            query += " WHERE(p.{})".format(where)
        query += " SET p.{}".format(set)

        return self.redis_connection.execute_command("GRAPH.QUERY",
                                                     self.graph_name,
                                                     query)

    def create_relation(self, label_source: str, where_source: str,
                        relation_type: str, label_dest: str,
                        where_dest: str) -> list:
        """
        Create a relation(edge) between nodes according to WHERE filters
        and the relation_type given.
        """
        query = "MATCH(s:{} {{{}}}), ".format(label_source, where_source)
        query += "(d:{} {{{}}})".format(label_dest, where_dest)
        query += " CREATE (s)-[:{}]->(d)".format(relation_type)
        return self.redis_connection.execute_command("GRAPH.QUERY",
                                                     self.graph_name,
                                                     query)

    def add_node(self, label: str, alias: str, properties: dict) -> Node:
        """
        Add node to the redis graph
        :param label1: label for the node.
        :param alias1: alias for the node.
        :param properties: properties for the node.
        :return: Created Node
        """
        node = Node(label=label, alias=alias, properties=properties)
        self.redis_graph.add_node(node)
        return node

    def add_edge(self, source_node: Node, predicate: str,
                 dest_node: str) -> None:
        """Add edge between nodes in redis graph
        :param source_node: source node of the edge.
        :param predicate: relationship between the source and destination node
        :param dest_node: destination node of the edge.
        """
        edge = Edge(source_node, predicate, dest_node)
        self.redis_graph.add_edge(edge)

    def commit(self) -> None:
        """Commit the changes made to the Graph to Redi"""
        self.redis_graph.commit()

    def process_output(self, get_data: list) -> list:
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