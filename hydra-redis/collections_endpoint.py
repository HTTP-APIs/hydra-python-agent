import urllib.request as ur
import json
import re
from redisgraph import Node, Edge
from classes_objects import Classes


class Collections:
    """Contains all the collections endpoints and objects"""

    def __init__(self, redis_graph):
        self.redis_graph = redis_graph

    def collectionobjects(
            self,
            obj_collection_node,
            new_file,
            new_url,
            url_node,
            api_doc,
            base_url):
        """Creating nodes for all objects stored in collection."""
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
                match_obj = re.match(
                    r'/(.*)/(.*)/(.*)?', obj["@id"], re.M | re.I)
                base_url = "/{0}/{1}/".format(match_obj.group(1),
                                              match_obj.group(2))
                entrypoint_member = obj["@type"].lower() + match_obj.group(3)
                print(base_url, entrypoint_member)
                member_alias = entrypoint_member
                # key for the object node is memeber_alias
                member_id = match_obj.group(3)
                print("event alias and id", member_alias, member_id)
                new_url1 = new_url + "/" + member_id
                response = ur.urlopen(new_url1)
                new_file1 = json.loads(response.read().decode('utf-8'))
                # object data retrieving from the server
                if obj["@type"] in api_doc.parsed_classes:
                    for obj2 in api_doc.parsed_classes[obj["@type"]
                                                       ]["class"
                                                         ].supportedOperation:
                        obj_method.append(obj2.method)
                    obj_properties["methods"] = str(obj_method)
                    # all the operations for the object is stored in method
                    for obj2 in api_doc.parsed_classes[obj["@type"]
                                                       ]["class"
                                                         ].supportedProperty:
                        if obj2.prop.replace(
                                "vocab:", "") in api_doc.parsed_classes:
                            obj_prop.append(obj2.prop.replace("vocab:", ""))
                    obj_properties_classlist = obj_prop
                    obj_properties["class_property"] = str(
                        obj_properties_classlist)
                    # all property which itself is an object
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
                    label="objects",
                    alias=str(member_alias),
                    properties=obj_properties)
                self.redis_graph.add_node(objects_node)
                # add object as a node in redis
#                print("commiting collection object", member_alias)
#                self.redis_graph.commit()
#                print(
#                    "property of obj which can be class")
                edge = Edge(obj_collection_node, "has_" +
                            str(obj["@type"]),
                            objects_node)
                self.redis_graph.add_edge(edge)
                # set an edge between the collection and its object
#                print("commiting collection object", member_alias)
#                self.redis_graph.commit()
                # put/create the graph in redis
                print(
                    "property of obj which can be class",
                    obj_properties["class_property"],
                    "collection"
                )

                if obj_properties_classlist:
                    c = Classes(self.redis_graph)
                    c.objects_property(
                        objects_node,
                        obj_properties_classlist,
                        url_node,
                        api_doc)
        else:
            print("NO MEMBERS")

    def endpointCollection(
            self,
            collection_endpoint,
            url_node,
            api_doc,
            base_url):
        """It makes a node for every collection endpoint."""
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
            # url for every collection endpoint
            for obj2 in api_doc.collections[
                                            obj][
                                            "collection"].supportedOperation:
                obj_method.append(obj2.method)
            obj_properties["methods"] = str(obj_method)
            # all the operations for the collection endpoint is stored in
            # method
            print(obj_properties["methods"])
            for obj2 in api_doc.collections[
                                            obj][
                                            "collection"].supportedProperty:
                properties.append(str(obj2.desc[4:]))
            obj_properties["title"] = str(properties)
            response = ur.urlopen(base_url + collection_endpoint[obj])
            new_file = json.loads(response.read().decode('utf-8'))
            # retrieving the objects from the collection endpoint
            obj_properties["members"] = str(new_file["members"])
            obj_collection_node = Node(
                label="collection", alias=obj, properties=obj_properties)
            self.redis_graph.add_node(obj_collection_node)
            edge = Edge(url_node, "has_collection", obj_collection_node)
            self.redis_graph.add_edge(edge)
            # set an edge between the entrypoint and collection endpoint
#            print("commit endpoint collection")
#            self.redis_graph.commit()
            # create the graph in redis
            self.collectionobjects(
                obj_collection_node,
                new_file["members"],
                new_url,
                url_node,
                api_doc,
                base_url
            )
