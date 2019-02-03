from redisgraph import Node, Edge


class GraphFunctions:
    """
    Used for invoking functions on redis_graph

    Attributes:
        redis_graph: Redis Graph for the API Documentation
        api_doc: HydraDoc object of the API Documentation
    """

    def __init__(self, redis_graph, api_doc):
        self.redis_graph = redis_graph
        self.api_doc = api_doc

    def addNode(self, label, alias, properties):
        """
        Adds a node to the redis graph.

        Args:
            label: Label for the Node.
            alias: Alias for the Node.
            properties: Properties of the Node.
        Returns:
            Node object created by the function.
        """
        node = Node(label=label, alias=alias, properties=properties)
        try:
            self.redis_graph.add_node(node)
        except Exception as err:
            raise err
        return node

    def addEdge(self, subject_node, predicate, object_node):
        """Add edge between 2 nodes in the redis graph.

        Args:
            subject_node: Subject of the new triple.
            predicate: Predicate of the new triple.
            object_node: Object of the new triple.
        """
        edge = Edge(subject_node, predicate, object_node)
        try:
            self.redis_graph.add_edge(edge)
        except Exception as err:
            raise err
