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
    """ open the given url and read and load the Json data.
    """
    response = ur.urlopen(url)
    return json.loads(response.read().decode('utf-8'))


def objects_property(objects_node, new_list, url_node):
    """makes nodes for those properties which have properties in itself.
    """
    print("for the properties which have class and should have node")
    print(new_list)
    for obj in new_list:
        obj_method = []
        obj_prop = []
        properties = []
        obj = obj.replace("vocab:", "")
        objects_properties = {}
        for obj1 in api_doc.parsed_classes[obj]["class"].supportedOperation:
            obj_method.append(obj1.method)
        print("classes", obj_method)
        objects_properties["methods"] = str(obj_method)
        for obj1 in api_doc.parsed_classes[obj]["class"].supportedProperty:
            properties.append(obj1.title)
            if obj1.prop.replace("vocab:", "") in api_doc.parsed_classes:
                obj_prop.append(obj1.prop.replace("vocab:", ""))
        objects_properties["property"] = str(properties)
        obj_properties_classlist = obj_prop
        objects_properties["class_property"] = str(
            obj_properties_classlist)
        print(objects_node.alias + str(obj))
        obj_alias = str(objects_node.alias + str(obj)).lower()
        print(obj_alias)
        obj_node = Node(
            label="id",
            alias=obj_alias,
            properties=objects_properties)
        redis_graph.add_node(obj_node)
        edge = Edge(objects_node, "has" + str(obj), obj_node)
        redis_graph.add_edge(edge)
        if obj_properties_classlist:
            objects_property(
                obj_node, obj_properties_classlist, url_node)


def endpointclasses(classes_endpoint, url_node):
    """node for every class which have an endpoint.
    """
    print("classes endpoint or accessing classes")

    for obj in classes_endpoint:
        obj_method = []
        obj_prop = []
        properties = []
        obj_properties = {}
        member = {}
        print("check endpoint url....loading data")
        new_url = base_url + classes_endpoint[obj]
        print(new_url)
        response = ur.urlopen(new_url)
        new_file = json.loads(response.read().decode('utf-8'))
        if obj in api_doc.parsed_classes:
            for obj1 in api_doc.parsed_classes[obj]["class"
                                                    ].supportedOperation:
                obj_method.append(obj1.method)
            print("classes ", obj_method)
            obj_properties["methods"] = str(obj_method)
            for obj1 in api_doc.parsed_classes[obj]["class"].supportedProperty:
                properties.append(obj1.title)
                if obj1.prop.replace("vocab:", "") in api_doc.parsed_classes:
                    obj_prop.append(obj1.prop.replace("vocab:", ""))
            obj_properties["property"] = str(properties)
            obj_properties_classlist = obj_prop
            obj_properties["class_property"] = str(
                obj_properties_classlist)

            for obj1 in api_doc.parsed_classes[obj]["class"].supportedProperty:
                if isinstance(new_file[obj1.title], str):
                    member[obj1.title] = str(
                        new_file[obj1.title].replace(" ", ""))

        member["@id"] = str(new_file["@id"])
        member["@type"] = str(new_file["@type"])
        obj_properties["property"] = str(member)
        class_object_node = Node(
            label="id",
            alias=str(obj),
            properties=obj_properties)
        redis_graph.add_node(class_object_node)
        edge = Edge(url_node, "has" + obj, class_object_node)
        redis_graph.add_edge(edge)
        if obj_properties_classlist:
            print("in obj_properties_classlist", obj_properties_classlist)
            objects_property(
                class_object_node,
                obj_properties_classlist,
                url_node)


def collectionobjects(obj_collection_node, new_file, new_url, url_node):
    """creating nodes for all objects stored in collection.
    """
    objects = new_file
    if isinstance(objects, str):
        objects = objects.replace("[", "")
        objects = objects.replace("]", "")

    obj_properties = {}
    print("accesing the collection object like events or drones")
    if objects:
        for obj in objects:
            obj_prop = []
            obj_method = []
            member = {}
            match_obj = re.match(r'/(.*)/(.*)/(.*)?', obj["@id"], re.M | re.I)
            base_url = "/{0}/{1}/".format(match_obj.group(1),
                                          match_obj.group(2))
            entrypoint_member = obj["@type"].lower() + match_obj.group(3)
            print(base_url, entrypoint_member)
            member_alias = entrypoint_member
            member_id = match_obj.group(3)
            print("event alias and id", member_alias, member_id)
            new_url1 = new_url + "/" + member_id
            response = ur.urlopen(new_url1)
            new_file1 = json.loads(response.read().decode('utf-8'))
            if obj["@type"] in api_doc.parsed_classes:
                for obj2 in api_doc.parsed_classes[obj["@type"]
                                                   ]["class"
                                                     ].supportedOperation:
                    obj_method.append(obj2.method)
                obj_properties["methods"] = str(obj_method)
                for obj2 in api_doc.parsed_classes[obj["@type"]
                                                   ]["class"
                                                     ].supportedProperty:
                    if obj2.prop.replace(
                            "vocab:", "") in api_doc.parsed_classes:
                        obj_prop.append(obj2.prop.replace("vocab:", ""))
                obj_properties_classlist = obj_prop
                obj_properties["class_property"] = str(
                    obj_properties_classlist)
                for obj1 in api_doc.parsed_classes[obj["@type"]
                                                   ]["class"
                                                     ].supportedProperty:
                    if isinstance(new_file1[obj1.title], str):
                        member[obj1.title] = str(
                            new_file1[obj1.title].replace(" ", ""))

            member["@id"] = str(obj["@id"])
            member["@type"] = str(obj["@type"])
            obj_properties["property"] = str(member)
            objects_node = Node(
                label="id",
                alias=str(member_alias),
                properties=obj_properties)
            redis_graph.add_node(objects_node)
            print("commiting collection object", member_alias)
            redis_graph.commit()
            print(
                "property of obj which can be class")
            edge = Edge(obj_collection_node, "has_" +
                        str(obj["@type"]),
                        objects_node)
            redis_graph.add_edge(edge)
            print("commiting collection object", member_alias)
            redis_graph.commit()
            print(
                "property of obj which can be class",
                obj_properties["class_property"],
                "collection"
            )
            if obj_properties_classlist:
                objects_property(
                    objects_node,
                    obj_properties_classlist,
                    url_node)
    else:
        print("NO MEMBERS")


def endpointCollection(collection_endpoint, url_node):
    """it makes a node for every collection endpoint.
    """
    print("accessing every collection in entrypoint")
    for obj in collection_endpoint:
        obj_method = []
        properties = []
        obj_properties = {}
        print(
            "check url for endpoint",
            base_url +
            collection_endpoint[obj])
        new_url = base_url + collection_endpoint[obj]
        for obj2 in api_doc.collections[obj]["collection"].supportedOperation:
            obj_method.append(obj2.method)
        obj_properties["methods"] = str(obj_method)
        print(obj_properties["methods"])
        for obj2 in api_doc.collections[obj]["collection"].supportedProperty:
            properties.append(str(obj2.desc[4:]))
        obj_properties["title"] = str(properties)
        response = ur.urlopen(base_url + collection_endpoint[obj])
        new_file = json.loads(response.read().decode('utf-8'))
        obj_properties["members"] = str(new_file["members"])
        obj_collection_node = Node(
            label="id", alias=obj, properties=obj_properties)
        redis_graph.add_node(obj_collection_node)
        edge = Edge(url_node, "has_collection", obj_collection_node)
        redis_graph.add_edge(edge)
        collectionobjects(
            obj_collection_node,
            new_file["members"],
            new_url,
            url_node)


def get_apistructure(entrypoint_obj, url_node):
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
        endpointCollection(collection_endpoint, url_node)

    if classes == 1:
        endpointclasses(classes_endpoint, url_node)


def get_endpoints(entrypoint_obj):
    """create node for entrypoint"""
    print("creating entrypoint node")
    url_node = Node(label="id", alias="Entrypoint", properties=entrypoint_obj)
    redis_graph.add_node(url_node)
    return get_apistructure(entrypoint_obj, url_node)


if __name__ == "__main__":
    url = "http://35.224.198.158:8080/api"
    match_obj = re.match(r'(.*)://(.*)/(.*)/?', url, re.M | re.I)
    base_url = "{0}://{1}".format(match_obj.group(1), match_obj.group(2))
    entrypoint = "/" + match_obj.group(3) + "/"
    print("baseurl, entrypoint ", base_url, entrypoint)

    apidoc = final_file(url + "/vocab")
    api_doc = doc_maker.create_doc(apidoc)
    get_endpoints(api_doc.entrypoint.get())
    print("commiting")
    redis_graph.commit()
    print("done!!!!")

#    for edge in redis_graph.edges:
#        print(edge)
