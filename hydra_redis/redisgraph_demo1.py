import redis
from redisgraph import Graph, Node, Edge
import urllib.request as ur
import json
import re
from re import compile as regex
from httplib2 import Http
from hydrus.hydraspec import doc_maker


redis_con = redis.Redis(host='localhost', port=6379)
redis_graph = Graph("apidoc", redis_con)


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
    response = ur.urlopen(url)
    new_file = json.loads(response.read().decode('utf-8'))
    return new_file


def get_method(new_obj):
    obj_method = []
    for obj in new_obj:
        obj_method.append(obj["method"].lower())
    return obj_method


def get_title(new_obj):
    new_obj = new_obj[0]
#    print (new_obj)
    obj_title = new_obj["description"]
    print(obj_title)
    return str(obj_title[4:])


def get_endpoint_id(string):
    return (string.replace("vocab:EntryPoint", ""))


def get_member_alias(string1, string2):
    match_obj = re.match(r'/(.*)/(.*)/(.*)?', string1, re.M | re.I)
    base_url = "/{0}/{1}/".format(match_obj.group(1), match_obj.group(2))
    entrypoint_member = string2 + match_obj.group(3)
    print(base_url, entrypoint_member)
    return entrypoint_member, match_obj.group(3)


def remove_vocab(string):
    return string.replace("vocab:", "")


def get_property(new_obj):
    obj_prop = []
    for obj in new_obj:
        for obj1 in apidoc["supportedClass"]:
            if obj1["@id"] == obj["property"]:
                print(obj_prop, obj["property"])
                obj_prop.append(obj["property"])
    if obj_prop:
        return obj_prop
    else:
        return []


def connect_nodes(source_node, predicate, dest_node):
    edge = Edge(source_node, predicate, dest_node)
    redis_graph.add_edge(edge)
    print("add edge commit", predicate)
    redis_graph.commit()
    print("edge", edge)


def objects_property(objects_node, new_list, url_node):
    print("for the properties which have class and should have node")

    for obj in new_list:
        objects_properties = {}
        for obj1 in apidoc["supportedClass"]:
            if obj1["@id"] == obj:
                properties = []
                if obj1["supportedOperation"]:
                    objects_properties["methods"] = str(
                        get_method(obj1["supportedOperation"]))
                if obj1["supportedProperty"]:
                    for obj2 in obj1["supportedProperty"]:
                        properties.append(obj2["title"])
                    objects_properties["property"] = str(properties)
                    obj_properties_classlist = get_property(
                        obj1["supportedProperty"])
                    objects_properties["class_property"] = str(
                        obj_properties_classlist)
        print(objects_node.alias + remove_vocab(obj))
        obj_alias = str(objects_node.alias + remove_vocab(obj)).lower()
        obj_node = Node(
            label="id",
            alias=obj_alias,
            properties=objects_properties)
        redis_graph.add_node(obj_node)
        print("commiting objects_property", obj_node)
        redis_graph.commit()
        print("property node", obj_node)
        edge = Edge(objects_node, "has" + remove_vocab(obj), obj_node)
        redis_graph.add_edge(edge)
        print("commiting objects_property edge", obj_node)
        redis_graph.commit()
        print("property node", obj_node)
        connect_nodes(url_node, "has" +
                      str(objects_node.alias +
                          remove_vocab(obj)), obj_node)
        if obj_properties_classlist:
            return objects_property(
                obj_node, obj_properties_classlist, url_node)
        else:
            return None
#    print (obj_node,new_list)


def endpointclasses(classes_node, url_node):
    print("classes endpoint or accessing classes")
    for obj in classes_node.properties:
        obj_properties = {}
        member = {}
        print("check endpoint url....loading data")
        new_url = base_url + classes_node.properties[obj]
        print(new_url)
        response = ur.urlopen(new_url)
        new_file = json.loads(response.read().decode('utf-8'))
        print(new_url, new_file)
        for obj1 in apidoc["supportedClass"]:
            if obj == obj1["title"]:
                obj_properties["methods"] = str(
                    get_method(obj1["supportedOperation"]))
                obj_properties_classlist = get_property(
                    obj1["supportedProperty"])
                obj_properties["class_property"] = str(
                    obj_properties_classlist)

                for obj2 in obj1["supportedProperty"]:
                    if isinstance(new_file[obj2["title"]], str):
                        member[obj2["title"]] = str(
                            new_file[obj2["title"]].replace(" ", ""))

        member["@id"] = str(new_file["@id"])
        member["@type"] = str(new_file["@type"])
        obj_properties["property"] = str(member)
        class_object_node = Node(
            label="id",
            alias=str(obj),
            properties=obj_properties)
        redis_graph.add_node(class_object_node)
        print("classes objects commiting edgee")
        redis_graph.commit()
        edge = Edge(classes_node, "has" + obj, class_object_node)
        redis_graph.add_edge(edge)
        print("classes objects commiting")
        redis_graph.commit()
        print("classes object node", class_object_node)
        connect_nodes(url_node, "has" + obj, class_object_node)
        print(obj_properties_classlist, edge)
        if obj_properties_classlist:
            print("in obj_properties_classlist", obj_properties_classlist)
            objects_property(
                class_object_node,
                obj_properties_classlist,
                url_node)


def collectionobjects(obj_collection_node, new_file, new_url, url_node):
    objects = new_file
    if isinstance(objects, str):
        objects = objects.replace("[", "")
        objects = objects.replace("]", "")

    obj_properties = {}
    member = {}
    print("accesing the collection object like events or drones")
    if objects:
        for obj in objects:
            member_alias, member_id = get_member_alias(
                obj["@id"], obj_collection_node.properties["title"])
            print("event alias and id", member_alias, member_id)
            new_url1 = new_url + "/" + member_id
            response = ur.urlopen(new_url1)
            new_file1 = json.loads(response.read().decode('utf-8'))
            for obj1 in apidoc["supportedClass"]:
                if obj["@type"] == remove_vocab(obj1["@id"]):
                    obj_properties["methods"] = str(
                        get_method(obj1["supportedOperation"]))
                    obj_properties_classlist = get_property(
                        obj1["supportedProperty"])
                    obj_properties["class_property"] = str(
                        obj_properties_classlist)
                    for obj2 in obj1["supportedProperty"]:
                        if isinstance(new_file1[obj2["title"]], str):
                            member[obj2["title"]] = str(
                                new_file1[obj2["title"]].replace("'", ""))

            member["@id"] = str(obj["@id"])
            member["@type"] = str(obj["@type"])
            obj_properties["property"] = str(member)
            objects_node = Node(
                label="id",
                alias=str(member_alias),
                properties=obj_properties)
            redis_graph.add_node(objects_node)
            edge = Edge(obj_collection_node, "has_" +
                        str(obj_collection_node.properties["title"]),
                        objects_node)
            redis_graph.add_edge(edge)
            print("commiting collection object", member_alias)
            redis_graph.commit()
            print(
                "property of obj which can be class",
                obj_properties["class_property"],
                "collection",
                obj1["@id"])
            connect_nodes(url_node, "has" + member_alias, objects_node)
            if obj_properties_classlist:
                objects_property(
                    objects_node,
                    obj_properties_classlist,
                    url_node)
    else:
        print("NO MEMBERS")


def endpointCollection(collection_node, url_node):
    print("accessing every collection in entrypoint")
    for obj in collection_node.properties:
        obj_properties = {}
        print(
            "check url for endpoint",
            base_url +
            collection_node.properties[obj])
        new_url = base_url + collection_node.properties[obj]
        print(
            "collection classes",
            api_doc.collections[obj]["collection"].generate())
        obj1 = api_doc.collections[obj]["collection"].generate()
        obj_properties["methods"] = str(get_method(obj1["supportedOperation"]))
        obj_properties["title"] = str(get_title(obj1["supportedProperty"]))
        response = ur.urlopen(base_url + collection_node.properties[obj])
        new_file = json.loads(response.read().decode('utf-8'))
        obj_properties["members"] = str(new_file["members"])
        obj_collection_node = Node(
            label="id", alias=obj, properties=obj_properties)
        redis_graph.add_node(obj_collection_node)
        edge = Edge(collection_node, "has_collection", obj_collection_node)
        redis_graph.add_edge(edge)
        print("commit endpointcollection")
        redis_graph.commit()
        print("every collection obj node ", obj_collection_node)
        connect_nodes(url_node, "has" + obj, obj_collection_node)
        collectionobjects(
            obj_collection_node,
            new_file["members"],
            new_url,
            url_node)


def get_apistructure(entrypoint_obj, url_node):
    collection_endpoint = {}
    classes_endpoint = {}
    collection = 0
    classes = 0
    print("split entrypoint into 2 types of endpoints collection and classes")
    for obj in url_node.properties:
        if obj != "@id" and obj != "@type" and obj != "@context":
            if obj in api_doc.collections.keys():
                collection = 1
#                print ("collection ddddd",new_obj)
                collection_endpoint[obj] = str(url_node.properties[obj])
            else:
                classes = 1
                classes_endpoint[obj] = str(url_node.properties[obj])
    if collection == 1:
        collection_node = Node(
            label="id",
            alias="collection_endpoint",
            properties=collection_endpoint)
        redis_graph.add_node(collection_node)
        edge = Edge(url_node, "has_collection_endpoint", collection_node)
        redis_graph.add_edge(edge)
#        redis_graph.commit()
        print("collection endpoint node ", collection_node)
        endpointCollection(collection_node, url_node)
#        redis_graph.commit()
    if classes == 1:
        classes_node = Node(
            label="id",
            alias="classes_endpoint",
            properties=classes_endpoint)
        redis_graph.add_node(classes_node)
        edge = Edge(url_node, "has_classes_endpoint", classes_node)
        redis_graph.add_edge(edge)
        print("classes endpoint node", classes_node)
        endpointclasses(classes_node, url_node)
#        redis_graph.commit()


def get_endpoints(entrypoint_obj):
    print("creating entrypoint node")
    url_node = Node(label="id", alias="Entrypoint", properties=entrypoint_obj)
    redis_graph.add_node(url_node)
    print("commiting")
    redis_graph.commit()
    print("entrypoint node ", url_node)
    get_apistructure(entrypoint_obj, url_node)


url = "http://35.224.198.158:8080/api"
match_obj = re.match(r'(.*)://(.*)/(.*)/?', url, re.M | re.I)
base_url = "{0}://{1}".format(match_obj.group(1), match_obj.group(2))
entrypoint = "/" + match_obj.group(3) + "/"
print(base_url, entrypoint)


apidoc = final_file(url + "/vocab")
api_doc = doc_maker.create_doc(apidoc)
get_endpoints(api_doc.entrypoint.get())
print("commiting")
redis_graph.commit()
print("done!!!!")

""" use it for checking the structure of graph with edges"""
#for edge in redis_graph.edges:
#    print(edge)

