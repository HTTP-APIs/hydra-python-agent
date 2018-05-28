"""
*Readme for this file*:
 It contains a graph which contain the api structure of api doc
 It design with the help of endpoints and its operation
 Design:
  url or id => endpoints[] => collection(get) and classes(put or post)
                             ((if collection then => classes=> members(get))
                             elif classes then =>members(get))


"""


import redis
from redisgraph import Graph, Node, Edge
import urllib
import json
import re
from re import compile as regex
from httplib2 import Http

redis_con = redis.Redis(host='localhost', port=6379)
redis_graph = Graph("apidoc", redis_con)
"""
getting the apidoc
"""


class _MemCache(dict):

    def __nonzero__(self):
        # even if empty, a _MemCache is True
        return True

    def set(self, key, value):
        self[key] = value

    def delete(self, key):
        if key in self:
            del self[key]


DEFAULT_HTTP_CLIENT = Http(_MemCache())
http = DEFAULT_HTTP_CLIENT
APIDOC_RE = regex(
    r'^<([^>]*)>; rel="http://www.w3.org/ns/hydra/core#apiDocumentation"$')


def final_file(url):
    response = urllib.urlopen(url)
    new_file = json.loads(response.read())
    return check_url(new_file, url)


def check_url(new_file, url):
    response, content = http.request(url, "GET")
    link = response.get('link')
    match = APIDOC_RE.match(link)
    api_doc = match.groups()[0]
    if api_doc != url:
        print url, "not match", api_doc
        new_url = api_doc
        return final_file(new_url)
    else:
        return new_file


url = "http://www.markus-lanthaler.com/hydra/event-api/"
match_obj = re.match(r'(.*)://(.*)/(.*)/(.*)/(.*)/?', url, re.M | re.I)
base_url = "{0}://{1}".format(match_obj.group(1), match_obj.group(2))
entrypoint = "/" + match_obj.group(3) + "/" + match_obj.group(4) + "/"

apidoc = final_file(url)

"""
extracting the endpoints and some of its properties or its api structure
"""


def get_endpoint_id(string):
    return (entrypoint + string.replace("vocab:EntryPoint/", ""))


def get_member_alias(string):
    match_obj = re.match(r'/(.*)/(.*)/(.*)/(.*)?', string, re.M | re.I)
#    base_url = "/{0}/{1}/".format(match_obj.group(1), match_obj.group(2))
    entrypoint_member = "member" + match_obj.group(4)
    return entrypoint_member


def remove_vocab(string):
    return string.replace("vocab:", "")


""" Finding the entrypoint class for extracting the endpoints"""

for obj in apidoc["supportedClass"]:
    if obj["@id"] == "vocab:EntryPoint":
        entrypoint_obj = obj
        break
# print entrypoint_obj["@id"]
endpoints = {}
endpoint_list = []
for obj in entrypoint_obj["supportedProperty"]:
    endpoint = {}
    new_obj = obj["property"]
    endpoint["title"] = obj["hydra:title"]
    endpoint["id"] = new_obj["@id"]
    endpoints[endpoint["title"]] = str(get_endpoint_id(endpoint["id"]))
    endpoint_list.append(endpoint["id"])
endpoints["@id"] = str(url)
endpoints["@type"] = "EntryPoint"
url_node = Node(label="id", alias="url", properties=endpoints)
redis_graph.add_node(url_node)

""" Creating endpoints as the nodes and set all the properties or
    data with the help of endpoint """

for obj in entrypoint_obj["supportedProperty"]:
    endpoint = {}
    get_endpoint = 0
    post_endpoint = 0
    put_endpoint = 0
    post_collection = 0
    put_collection = 0
    put_classes = 0
    post_classes = 0
    delete_classes = 0
    get_classes = 0
    new_obj = obj["property"]
    endpoint["@id"] = str(get_endpoint_id(new_obj["@id"]))
    endpoint["@type"] = str(remove_vocab(new_obj["range"]))
    response = urllib.urlopen(base_url + endpoint["@id"])
    new_file = json.loads(response.read())
    endpoint["members"] = str(new_file["members"])
    node = Node(
        label="endpoint",
        alias=str(
            obj["hydra:title"]),
        properties=endpoint)
    redis_graph.add_node(node)
    edge = Edge(url_node, "has_endpoint", node)
    redis_graph.add_edge(edge)

    """ for keeping track of the operations we have to use some flags
        with these help as we'll be able to perform operation on that.
        And collection and classes have different nodes """

    for new_obj_op in new_obj["supportedOperation"]:
        if new_obj_op["method"] == "GET":
            get_endpoint = 1
            returns = new_obj_op["returns"]
            collection_node = Node(
                label="id",
                alias="collection",
                properties=node.properties)
            redis_graph.add_node(collection_node)
            edge = Edge(node, "get_method", collection_node)
            redis_graph.add_edge(edge)
            # get_function(node) which shows the properties of node
        elif new_obj_op["method"] == "POST":
            post_endpoint = 1
            return_class = new_obj_op["returns"]
            class_node = Node(
                label="id",
                alias="classes",
                properties=node.properties)
            redis_graph.add_node(class_node)
            edge = Edge(node, "post_method", class_node)
            redis_graph.add_edge(edge)
            # here we'll call a function for post the endpoint
        elif new_obj_op["method"] == "PUT":
            put_endpoint = 1
            return_class = new_obj_op["returns"]
            class_node = Node(
                label="id",
                alias="classes",
                properties=node.properties)
            redis_graph.add_node(class_node)
            edge = Edge(node, "put_method", class_node)
            redis_graph.add_edge(edge)
    if post_endpoint == 0 and put_endpoint == 0:
        flag = 0
        for obj in apidoc["supportedClass"]:
            if obj["@id"] == returns:
                flag = 1
                collection = obj
        if flag == 1:
            for obj in collection["supportedOperation"]:
                if obj["method"] == "POST" or obj["method"] == "PUT":
                    return_class = obj["returns"]
                    class_node = Node(
                        label="id",
                        alias="classes",
                        properties=node.properties)
                    redis_graph.add_node(class_node)
                    break
                if obj["method"] == "POST":
                    post_collection = 1
                if obj["method"] == "PUT":
                    put_collection = 1

    """ connect the collection to the classes by edge"""

    edge = Edge(collection_node, "has_classes", class_node)
    redis_graph.add_edge(edge)
    if (post_endpoint == 1 or
            put_endpoint == 1 or
            post_collection == 1 or
            put_collection == 1):
        flag = 0
        for obj in apidoc["supportedclass"]:
            if obj["@id"] == return_class:
                flag = 1
                classes = obj
        if flag == 1:
            for obj in classes["supportedOperation"]:
                if obj["method"] == "PUT":
                    put_classes = 1
                if obj["method"] == "POST":
                    post_classes = 1
                if obj["method"] == "DELETE":
                    delete_classes = 1
                if obj["method"] == "GET":
                    get_classes = 1

    """ members are leave nodes which is connect with the classes
        every elementary operation should be perform on these.
        like put,post,delete these operation can be done by adding and
        deleting the nodes and update all the above nodes properties"""

    for member in new_file["members"]:
        endpoint_member = {}
        endpoint_member["@id"] = str(member["@id"])
        response = urllib.urlopen(base_url + member["@id"])
        new_dict = json.loads(response.read())
        endpoint_member["@type"] = str(new_dict["@type"])
        endpoint_member["name"] = str(new_dict["name"])
        endpoint_member["description"] = str(new_dict["description"])
        endpoint_member["start_date"] = str(new_dict["start_date"])
        endpoint_member["end_date"] = str(new_dict["end_date"])
        endpoint_member_alias = str(get_member_alias(member["@id"]))
        print endpoint_member_alias
        node1 = Node(
            label="endpoint_member",
            alias=str(endpoint_member_alias),
            properties=endpoint_member)
        redis_graph.add_node(node1)
        edge = Edge(class_node, "class_get_member", node1)
        redis_graph.add_edge(edge)

""" creating the graph setup all the nodes and edges"""

print "commiting"
redis_graph.commit()
print "done!!!!"
# for node in redis_graph.edges:
#    print node
