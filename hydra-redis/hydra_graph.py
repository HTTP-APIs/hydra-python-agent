import redis
from redisgraph import Graph, Node
import urllib.request as ur
import json
import re
from hydrus.hydraspec import doc_maker
from graphviz import Digraph
from classes_objects import Classes
from collections_endpoint import Collections as collect


def final_file(url):
    """ Open the given url and read and load the Json data."""
    response = ur.urlopen(url)
    return json.loads(response.read().decode('utf-8'))


def get_apistructure(entrypoint_obj, url_node, api_doc):
    """ It breaks the endpoint into two parts collection and classes"""
    collection_endpoint = {}
    classes_endpoint = {}
    collection = 0
    classes = 0
    print("split entrypoint into 2 types of endpoints collection and classes")
    for obj in url_node.properties:
        if obj != "@id" and obj != "@type" and obj != "@context":
            if obj in api_doc.collections.keys():
                collection = 1
                collection_endpoint[obj] = str(url_node.properties[obj])
            else:
                classes = 1
                classes_endpoint[obj] = str(url_node.properties[obj])
    if collection == 1:
        coll = collect(redis_graph)
        coll.endpointCollection(
            collection_endpoint,
            url_node,
            api_doc,
            base_url)

    if classes == 1:
        clas = Classes(redis_graph)
        clas.endpointclasses(classes_endpoint, url_node, api_doc, base_url)


def get_endpoints(api_doc):
    """Create node for entrypoint"""
    print("creating entrypoint node")
    entrypoint_obj = api_doc.entrypoint.get()
    url_node = Node(label="id", alias="Entrypoint", properties=entrypoint_obj)
    redis_graph.add_node(url_node)
    return get_apistructure(entrypoint_obj, url_node, api_doc)


if __name__ == "__main__":
    redis_con = redis.Redis(host='localhost', port=6379)
    redis_graph = Graph("apidoc", redis_con)
    url = "http://35.224.198.158:8081/api"
    match_obj = re.match(r'(.*)://(.*)/(.*)/?', url, re.M | re.I)
    base_url = "{0}://{1}".format(match_obj.group(1), match_obj.group(2))
    entrypoint = "/" + match_obj.group(3) + "/"
    print("baseurl", base_url, " entrypoint", entrypoint)

    apidoc = final_file(url + "/vocab")
    api_doc = doc_maker.create_doc(apidoc)
    get_endpoints(api_doc)
    print("commiting")
    redis_graph.commit()
    # creating whole the graph in redis
    print("done!!!!")
    #uncomment below 2 lines for getting nodes for whole graph
#    for node in redis_graph.nodes:
#        print("\n",node)
    #uncomment the below lines for show the graph stored in redis
#    g = Digraph('redis_graph', filename='hydra_graph.gv')
#    # using graphviz for visualization of graph stored in redis
#    for edge in redis_graph.edges:
#        g.edge(edge.src_node.alias, edge.dest_node.alias)
#    g.view()
    # see the graph generaated by graphviz
