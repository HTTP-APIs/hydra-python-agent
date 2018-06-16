import redis
from redisgraph import Graph, Node, Edge
import urllib.request
import json
from graphviz import Digraph
import hydrus
from hydrus.hydraspec import doc_maker


def final_file(url):
    """ Open the given url and read and load the Json data."""
    response = urllib.request.urlopen(url)
    return json.loads(response.read().decode('utf-8'))


def addNode(node_label, node_alias, node_properties):
    """Add node to redis_graph and return the same node"""
    node = Node(
        label=node_label,
        alias=node_alias,
        properties=node_properties)
    redis_graph.add_node(node)
    return node


def addEdge(src_node, predicate, dest_node):
    """ Add an edge in between src_node and dest_node"""
    edge = Edge(src_node, predicate, dest_node)
    redis_graph.add_edge(edge)


def apistructure_collection(collection_endpoints, entrypoint_node):
    """ Getting the properties from APIdoc for collection endpoints"""
    for endpoint in collection_endpoints:
        endpoint_method = []
        node_properties = {}
        for support_operation in api_doc.collections[
                endpoint][
                "collection"].supportedOperation:
            endpoint_method.append(support_operation.method)
        node_properties["operations"] = str(endpoint_method)
        node_properties["@id"] = str(collection_endpoints[endpoint])
        node_properties["@type"] = str(endpoint)
        dest_node = addNode("collection", endpoint, node_properties)
        addEdge(entrypoint_node, "hasCollection", dest_node)


def apistructure_classes(class_endpoints, entrypoint_node):
    """ Getting the properties from APIdoc for class endpoints"""
    for endpoint in class_endpoints:
        node_properties = {}
        supported_properties_list = []
        endpoint_method = []
        node_properties["@id"] = str(class_endpoints[endpoint])
        node_properties["@type"] = str(endpoint)
        for support_operation in api_doc.parsed_classes[
                endpoint][
                "class"].supportedOperation:
            endpoint_method.append(support_operation.method)
        node_properties["operations"] = str(endpoint_method)
        for support_property in api_doc.parsed_classes[
                endpoint][
                "class"].supportedProperty:
            supported_properties_list.append(support_property.title)
        node_properties["properties"] = str(supported_properties_list)
        dest_node = addNode("class", endpoint, node_properties)
        addEdge(entrypoint_node, "hasClass", dest_node)


def get_apistructure(entrypoint_node):
    """ It breaks the endpoint into two parts collection and classes"""
    collection_endpoints = {}
    class_endpoints = {}
    collection = 0
    classes = 0
    print("split entrypoint into 2 types of endpoints collection and classes")
    for support_property in api_doc.entrypoint.entrypoint.supportedProperty:
        if isinstance(
                support_property,
                hydrus.hydraspec.doc_writer.EntryPointClass):
            class_endpoints[support_property.name] = support_property.id_
            collection = 1
        if isinstance(
                support_property,
                hydrus.hydraspec.doc_writer.EntryPointCollection):
            collection_endpoints[support_property.name] = support_property.id_
            classes = 1

    print("class_endpoints", class_endpoints)
    print("collection_endpoints", collection_endpoints)
    if classes == 1:
        apistructure_classes(class_endpoints, entrypoint_node)

    if collection == 1:
        apistructure_collection(
            collection_endpoints,
            entrypoint_node)


def get_entrypoint():
    """Getting tha properties for entrypoint"""
    entrypoint_properties = {}
    entrypoint_properties["@id"] = str("vocab:Entrypoint")
    entrypoint_properties["url"] = str(
        api_doc.entrypoint.url) + str(api_doc.entrypoint.api)
    entrypoint_properties["supportedOperation"] = "GET"
    entrypoint_node = addNode("id", "Entrypoint", entrypoint_properties)
    return get_apistructure(entrypoint_node)


def main(user, url):
    """ Setup the Redis connection and get api_doc with the help of hydrus"""
    redis_con = redis.Redis(host='localhost', port=6379, db=0)
    global redis_graph
    redis_graph = Graph(user, redis_con)
    apidoc = final_file(url + "/vocab")
    global api_doc
    api_doc = doc_maker.create_doc(apidoc)
    return get_entrypoint()


if __name__ == "__main__":
    user = input("user>>")
    url = input("url>>")
    print("lazyloading..... of graph")
    main(user, url)
    redis_graph.commit()
#    for node in redis_graph.nodes.values():
#        print(node)
    # uncomment below lines for view the graph
#    g = Digraph('redis_graph', filename='hydra_graph.gv')
#    # using graphviz for visualization of graph stored in redis
#    for edge in redis_graph.edges:
#        g.edge(edge.src_node.alias, edge.dest_node.alias)
#    g.view()
