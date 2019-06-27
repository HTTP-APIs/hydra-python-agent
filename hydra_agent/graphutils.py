import logging
from redisgraph import Node, Edge, Graph
from typing import Union, Optional
from redis.exceptions import ResponseError

logger = logging.getLogger(__file__)


class GraphUtils:

    def __init__(self, redis_proxy, graph_name="apigraph"):
        self.redis_proxy = redis_proxy
        self.redis_connection = redis_proxy.get_connection()
        self.graph_name = graph_name
        self.redis_graph = Graph(graph_name, self.redis_connection)

    def read(self, match: str, ret: str,
             where: Optional[str]=None) -> Union[list, None]:
        """
        Run query to read nodes in Redis and return the result
        :param match: Relationship between queried entities.
        :param ret: Defines which property/ies will be returned.
        :param where: Used to filter results, not mandatory.
        :return: Corresponding Nodes
        """
        query = "MATCH(p{})".format(match)
        if where is not None:
            query += " WHERE(p.{})".format(where)
        query += " RETURN p{}".format(ret)

        query_result = self.redis_graph.query(query)


        # Processing Redis-set response format
        query_result = self.process_result(query_result)
        
        if not query_result:
            query_result = None

        return query_result

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

    def delete(self, where: str, match: str = "") -> list:
        """
        Run query to update nodes in Redis and return the result
        :param match: Relationship between queried entities.
        :param set: The property to be updated.
        :param where: Used to filter results, not mandatory.
        :return: Query results
        """
        query = "MATCH(p{})".format(match)
        if where is not None:
            query += " WHERE(p.{})".format(where)
        query += " DELETE p"

        return self.redis_connection.execute_command("GRAPH.QUERY",
                                                     self.graph_name,
                                                     query)

    def create_relation(self, label_source: str, where_source: str,
                        relation_type: str, label_dest: str,
                        where_dest: str) -> list:
        """
        Create a relation(edge) between nodes according to WHERE filters.
        :param label_source: Source node label.
        :param where_source: Where statement to filter source node.
        :param relation_type: The name of the relation type to assign.
        :param label_dest: Label name for the destination node.
        :param where_dest: Where statement to filter destination node
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
        :param label: label for the node.
        :param alias: alias for the node.
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
        """Commit the changes made to the Graph to Redis"""
        self.redis_graph.commit()

    def process_result(self, result: list) -> list:
        """
        Partial data processing for results redis-sets
        :param get_data: data get from the Redis memory.
        """
        response_json_list = []

        for record in result.result_set[1:]:
            new_record = {}
            for j, property_x in enumerate(record):
                if property_x is None:
                    pass
                else:
                    property_name = result.result_set[0][j].decode()
                    try:
                        node_alias, property_name = property_name.split(".")
                        new_record[property_name] = property_x.decode()
                    except ValueError as e:
                        logger.info("Graph property with no dot/wrong format")
            if new_record:
                if 'id' in new_record:
                    new_record['@id'] = new_record.pop('id')
                    new_record['@type'] = new_record.pop('type')
                response_json_list.append(new_record)

        return response_json_list


if __name__ == "__main__":
    pass
 
