import redis
from redisgraph import Graph, Node, Edge
from httplib2 import Http, HttpLib2ErrorWithResponse
from re import compile as regex
import urllib
import json
import re
"""
**assumption**
we have to give alias also with every node because node is like ({label}:{alias} {{{properties}}}), it help us to identify the node. Now, alias is given to nodes and it is easy to understand the graph.
for no property of node we are using no_prop as dict and for know more about the id of node then try node.properties.
"""


def remove_special_character(string):
    if string[0:4] == "http":
        string = str(string[7:])
        return re.sub("[#@:./-]", "_", str(string))
    else:
        a = re.sub("[#@:./'-]", "_", str(string))
        return a.replace(" ", "_")


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
redis_con = redis.Redis(host='localhost', port=6379)
redis_graph = Graph("apidoc", redis_con)
no_prop = {"properties": "no property"}
null_node = Node(label="id", alias="empty", properties=no_prop)
redis_graph.add_node(null_node)


"""
final_file and check_url is used for check and find the vocab of the given url
"""


def final_file(url):
    response = urllib.urlopen(url)
    new_file = json.loads(response.read())
    check_url(new_file, url)


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
        prop = {"vocabid1": url}
        print api_doc, "yes match", url
        print "now we have to create the graph for ", url
        node_id = remove_special_character(new_file["@id"])
        node_url = Node(
            label="id1",
            alias=node_id,
            properties={
                "id1": str(
                    new_file["@id"])})
        redis_graph.add_node(node_url)
        get_type(new_file, node_url)
        return get_supp_class(node_url, "supportedclass",
                              new_file["supportedClass"])


"""
get_type returns type of vocab id
"""


def get_type(source_dict, source_node):
    predicate = "type"
    node_id = remove_special_character(source_dict["@type"])
    node = Node(
        label="id1_type",
        alias=node_id,
        properties={
            "id1_type": str(
                source_dict["@type"])})
    redis_graph.add_node(node)
    edge = Edge(source_node, predicate, node)
    redis_graph.add_edge(edge)


"""
we have to access supported class
"""
"""
get_supp_class is initial for getting into supportedClass and for access all other properties like supportedOpertion....
"""


def get_supp_class(source_node, predicate, new_file):
    count = 1
    for obj in new_file:
        idd = "id1_id" + str(count)
        value = "supportedcalss_id"
        count += 1
        node_id = remove_special_character(obj["@id"])
        node_supp_class_obj = Node(
            label=idd,
            alias=node_id,
            properties={
                idd: str(
                    obj["@id"])})
        redis_graph.add_node(node_supp_class_obj)
        edge = Edge(source_node, predicate, node_supp_class_obj)
        redis_graph.add_edge(edge)

        get_supp_class_value(obj, node_supp_class_obj)
    print "Creating the graph"
    redis_graph.commit()
    print "yess done"


"""link the every obj id to all of its properties"""


def get_supp_class_value(new_dict, source_node):
    for obj in new_dict:
        if obj != "@id":
            if not isinstance(new_dict[obj], list) and not isinstance(
                    new_dict[obj], dict):
                new_obj = remove_special_character(obj)
#                new_obj = ''.join(e for e in obj if e.isalnum())
                idd = source_node.label + "_" + new_obj
                if new_dict[obj]:
                    s = remove_special_character(new_dict[obj]).lower()
                else:
                    s = new_dict[obj]
                if s is None:
                    node_id = "none"
                else:
                    node_id = remove_special_character(s)
                node = Node(
                    label=idd,
                    alias=node_id,
                    properties={
                        str(idd): str(s)})
                redis_graph.add_node(node)
                edge = Edge(source_node, new_obj, node)
                redis_graph.add_edge(edge)

            elif obj == "supportedOperation":
                if new_dict[obj]:
                    get_supp_oper(new_dict[obj], source_node)
                else:
                    edge = Edge(source_node, obj, null_node)
                    redis_graph.add_edge(edge)

            elif obj == "supportedProperty":
                if new_dict[obj]:
                    get_supp_prop(new_dict[obj], source_node)
                else:
                    edge = Edge(source_node, obj, null_node)
                    redis_graph.add_edge(edge)


""" for supported operations"""


def get_supp_oper(new_file, source_node):
    predicate = "supportedoperation"
    count = 1
    for obj in new_file:
        idd = source_node.label + "_id1" + str(count)
        node_id = remove_special_character(obj["@id"])
        count += 1
        node_oper = Node(
            label=idd,
            alias=node_id,
            properties={
                idd: str(node_id)})
        redis_graph.add_node(node_oper)
        edge = Edge(source_node, predicate, node_oper)
        redis_graph.add_edge(edge)
        get_supp_oper_value(obj, node_oper)


def get_supp_oper_value(new_dict, source_node):
    for obj in new_dict:
        if obj != "@id":
            if not isinstance(new_dict[obj], list) and not isinstance(
                    new_dict[obj], dict):
                new_obj = remove_special_character(obj)
                idd = source_node.label + "_" + new_obj
                if new_dict[obj]:
                    s = remove_special_character(new_dict[obj]).lower()
                else:
                    s = new_dict[obj]
                if s is None or s == "delete":
                    node_id = "none"
                else:
                    node_id = s

                node = Node(
                    label=idd,
                    alias=node_id,
                    properties={
                        str(idd): str(s)})
                redis_graph.add_node(node)
                edge = Edge(source_node, new_obj, node)
                redis_graph.add_edge(edge)

            elif obj == "statusCodes":
                if new_dict[obj]:
                    get_status_code(new_dict[obj], source_node)
                else:
                    edge = Edge(source_node, obj, null_node)
                    redis_graph.add_edge(edge)


def get_status_code(new_file, source_node):
    predicate = "statuscodes"
    count = 1
    for obj in new_file:
        idd = source_node.label + "_id" + str(count)
        count += 1
        new_id = str(obj["code"])
        node_id = "_" + remove_special_character(new_id)
        node_status = Node(label=idd, alias=node_id, properties={idd: new_id})
        redis_graph.add_node(node_status)
        edge = Edge(source_node, predicate, node_status)
        redis_graph.add_edge(edge)
        get_status_code_value(obj, node_status)


def get_status_code_value(new_dict, source_node):
    for obj in new_dict:
        if obj != "code":
            if not isinstance(new_dict[obj], list) and not isinstance(
                    new_dict[obj], dict):
                idd = source_node.label + "_" + obj
                s = new_dict[obj]
                node_id = remove_special_character(s)
                node = Node(
                    label=idd,
                    alias=node_id,
                    properties={
                        str(idd): str(s)})
                redis_graph.add_node(node)
                edge = Edge(source_node, obj, node)
                redis_graph.add_edge(edge)


""" for supported property"""


def get_supp_prop(new_file, source_node):
    predicate = "supportedproperty"
    count = 1
    for obj in new_file:
        idd = source_node.label + "_id2" + str(count)
        count += 1
        new_id = remove_special_character(obj["hydra:title"])
        node_id = remove_special_character(new_id)
        node_prop = Node(
            label=idd, alias=node_id, properties={
                str(idd): str(new_id)})
        redis_graph.add_node(node_prop)
        edge = Edge(source_node, predicate, node_prop)
        redis_graph.add_edge(edge)
        get_supp_prop_value(obj, node_prop)


def get_supp_prop_value(new_dict, source_node):
    for obj in new_dict:
        if obj != "hydra:title":
            if not isinstance(new_dict[obj], list) and not isinstance(
                    new_dict[obj], dict):
                new_obj = remove_special_character(obj)
                idd = source_node.label + "_" + new_obj
                if new_dict[obj] and not isinstance(new_dict[obj], type(True)):
                    s = remove_special_character(new_dict[obj]).lower()
                else:
                    s = new_dict[obj]
                if s is None or s == "delete":
                    node_id = "none"
                elif str(s) == "True" or str(s) == "False":
                    node_id = "_" + str(s)
                else:
                    node_id = str(s)
                node = Node(
                    label=idd,
                    alias=node_id,
                    properties={
                        str(idd): str(s)})
                redis_graph.add_node(node)
                edge = Edge(source_node, new_obj, node)
                redis_graph.add_edge(edge)
            elif obj == "property" and isinstance(new_dict[obj], dict):
                get_prop(new_dict[obj], source_node)


def get_prop(new_dict, source_node):
    predicate = "property"
    idd = source_node.label + "_" + "property_id"
    s = remove_special_character(new_dict["@id"]).lower()
    node_id = s
    node_prop_id = Node(
        label=idd,
        alias=node_id,
        properties={
            str(idd): str(s)})
    redis_graph.add_node(node_prop_id)
    edge = Edge(source_node, predicate, node_prop_id)
    redis_graph.add_edge(edge)
    for obj in new_dict:
        if obj != "@id":
            if not isinstance(new_dict[obj], list) and not isinstance(
                    new_dict[obj], dict):
                new_obj = remove_special_character(obj)
                idd = source_node.label + "_" + new_obj
                if new_dict[obj] and not isinstance(new_dict[obj], type(True)):
                    s = remove_special_character(new_dict[obj]).lower()
                else:
                    s = new_dict[obj]
                node_id = remove_special_character(s)
                node = Node(
                    label=idd,
                    alias=node_id,
                    properties={
                        str(idd): str(s)})
                redis_graph.add_node(node)
                edge = Edge(node_prop_id, new_obj, node)
                redis_graph.add_edge(edge)

            elif obj == "supportedOperation":
                if new_dict[obj]:
                    get_supp_oper(new_dict[obj], node_prop_id)
                else:
                    edge = Edge(node_prop_id, obj, null_node)
                    redis_graph.add_edge(edge)


final_file("http://www.markus-lanthaler.com/hydra/event-api/")


""" showing the created graph using nodes and edges it can be easy to understand after seeing this file http://www.markus-   lanthaler.com/hydra/event-api/vocab/ """

print "showing nodes ------------------------------------------------------"
for i in redis_graph.nodes:
    print i
print "showing edges ------------------------------------------------------"
for j in redis_graph.edges:
    print j
