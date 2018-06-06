import urllib.request as ur
import json
from redisgraph import Node, Edge


class Classes:
    """Contains all the classes endpoint and the objects"""

    def __init__(self, redis_graph):
        self.redis_graph = redis_graph

    def objects_property(self, objects_node, new_list, url_node, api_doc):
        """Makes nodes for those properties which have properties in itself."""
        print("for the properties which have class and should have node")
        print(new_list)
        for obj in new_list:
            obj_method = []
            obj_prop = []
            properties = []
            obj = obj.replace("vocab:", "")
            objects_properties = {}
            for obj1 in api_doc.parsed_classes[
                                               obj][
                                               "class"].supportedOperation:
                obj_method.append(obj1.method)
            print("classes", obj_method)
            objects_properties["methods"] = str(obj_method)
            # all the operations for the object is stored in method
            for obj1 in api_doc.parsed_classes[obj]["class"].supportedProperty:
                properties.append(obj1.title)
                if obj1.prop.replace("vocab:", "") in api_doc.parsed_classes:
                    obj_prop.append(obj1.prop.replace("vocab:", ""))
            objects_properties["property"] = str(properties)
            # all property which itself is an object
            obj_properties_classlist = obj_prop
            objects_properties["class_property"] = str(
                obj_properties_classlist)
            print(objects_node.alias + str(obj))
            obj_alias = str(objects_node.alias + str(obj)).lower()
            # key for the node of the object
            print(obj_alias)
            obj_node = Node(
                label="object",
                alias=obj_alias,
                properties=objects_properties)
            self.redis_graph.add_node(obj_node)
            edge = Edge(objects_node, "has" + str(obj), obj_node)
            self.redis_graph.add_edge(edge)
            # set edge between the object and its parent object
#            print("commit object property")
#            self.redis_graph.commit()
            # create the graph in redis
            if obj_properties_classlist:
                self.objects_property(
                    obj_node, obj_properties_classlist, url_node, api_doc)

    def endpointclasses(self, classes_endpoint, url_node, api_doc, base_url):
        """Node for every class which have an endpoint."""
        print("classes endpoint or accessing classes")

        for obj in classes_endpoint:
            obj_method = []
            obj_prop = []
            properties = []
            obj_properties = {}
            member = {}
            print("check endpoint url....loading data")
            new_url = base_url + classes_endpoint[obj]
            # url for the classes endpoint
            print(new_url)
            response = ur.urlopen(new_url)
            new_file = json.loads(response.read().decode('utf-8'))
            # retreiving data for the classes endpoint from server
            if obj in api_doc.parsed_classes:
                for obj1 in api_doc.parsed_classes[obj]["class"
                                                        ].supportedOperation:
                    obj_method.append(obj1.method)
                print("classes ", obj_method)
                obj_properties["methods"] = str(obj_method)
                # store the operations for the endpoint
                for obj1 in api_doc.parsed_classes[obj]["class"
                                                        ].supportedProperty:
                    properties.append(obj1.title)
                    if obj1.prop.replace(
                            "vocab:", "") in api_doc.parsed_classes:
                        obj_prop.append(obj1.prop.replace("vocab:", ""))
                obj_properties["property"] = str(properties)
                obj_properties_classlist = obj_prop
                obj_properties["class_property"] = str(
                    obj_properties_classlist)
                # store all those properties which is itself an object
                for obj1 in api_doc.parsed_classes[obj]["class"
                                                        ].supportedProperty:
                    if isinstance(new_file[obj1.title], str):
                        member[obj1.title] = str(
                            new_file[obj1.title].replace(" ", ""))

            member["@id"] = str(new_file["@id"])
            member["@type"] = str(new_file["@type"])
            obj_properties["property"] = str(member)
            class_object_node = Node(
                label="classes",
                alias=str(obj),
                properties=obj_properties)
            self.redis_graph.add_node(class_object_node)
            edge = Edge(url_node, "has" + obj, class_object_node)
            self.redis_graph.add_edge(edge)
            # set edge between the entrypoint and the class endpoint/object
#            print("commit classesendpoint")
#            self.redis_graph.commit()
            # create the graph in redis
            if obj_properties_classlist:
                print("in obj_properties_classlist", obj_properties_classlist)
                self.objects_property(
                    class_object_node,
                    obj_properties_classlist,
                    url_node,
                    api_doc)
