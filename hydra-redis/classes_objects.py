import urllib.request
import json
from redisgraph import Node, Edge


class ClassEndpoints:
    """Contains all the classes endpoint and the objects"""

    def __init__(self, redis_graph):
        self.redis_graph = redis_graph

    def addNode(self, label1, alias1, properties1):
        """Add node to the redis graph"""
        node = Node(label=label1, alias=alias1, properties=properties1)
        self.redis_graph.add_node(node)
        return node

    def addEdge(self, source_node, predicate, dest_node):
        """Add edge between nodes in redis graph"""
        edge = Edge(source_node, predicate, dest_node)
        self.redis_graph.add_edge(edge)

    def get_operation(self, api_doc, endpoint):
        """Return all the supportedOperations for given endpoint"""
        endpoint_method = []

        for support_operation in api_doc.parsed_classes[
                endpoint][
                "class"].supportedOperation:
            endpoint_method.append(support_operation.method)
        print("supportedOperation", endpoint_method)
        # all the operations for the object is stored in endpoint_method

        return str(endpoint_method)

    def objects_property(
            self,
            objects_node,
            new_list,
            entrypoint_node,
            api_doc):
        """Nodes for every that property which is itself an object"""
        print("for the property which is an object, should be a node")
        for obj in new_list:
            obj = obj.replace("vocab:", "")
            node_properties = {}
            properties_title = []
            endpoint_prop = []
            # node_properties is used for set the properties of node.
            node_properties["operations"] = self.get_operation(api_doc, obj)
            for support_property in api_doc.parsed_classes[
                    obj][
                    "class"].supportedProperty:
                properties_title.append(support_property.title)
                if support_property.title in api_doc.parsed_classes:
                    endpoint_prop.append(support_property.title)
            # store all operation and property of object
            node_properties["property"] = str(properties_title)
            node_properties["class_property"] = str(
                endpoint_prop)
            node_alias = str(objects_node.alias + str(obj)).lower()
            # key for the node of the object
            object_node = self.addNode("object", node_alias, node_properties)
            print("node", object_node)
            self.addEdge(objects_node, "has" + str(obj), object_node)
            # set edge between the object and its parent object
            if endpoint_prop:
                self.objects_property(
                    object_node, endpoint_prop, entrypoint_node, api_doc)

    def endpointclasses(
            self,
            class_endpoints,
            entrypoint_node,
            api_doc,
            base_url):
        """Node for every class which have an endpoint."""
        print("classes endpoint or accessing classes")
        endpoint_property_list = {}
        # contain all endpoints which have other endpoints as a property.
        for endpoint in class_endpoints:
            node_properties = {}
            # node_properties is used for set the properties of node.
            member = {}
            # member contain the properties of class endpoint.
            endpoint_property = []
            # it contains the property which is a non-endpoint object or class.
            property_list = []
            print("check endpoint url....loading data")
            new_url = base_url + \
                class_endpoints[endpoint].replace("vocab:EntryPoint", "")
            # url for the classes endpoint
            print(new_url)
            response = urllib.request.urlopen(new_url)
            new_file = json.loads(response.read().decode('utf-8'))
            # retreiving data for the classes endpoint from server
            node_properties["operations"] = self.get_operation(
                api_doc, endpoint)
            # store the operations for the endpoint

            for support_property in api_doc.parsed_classes[
                                                   endpoint][
                                                   "class"].supportedProperty:
                if endpoint != support_property.title:
                    if support_property.title in class_endpoints:
                        property_list.append(support_property.title)
                    elif support_property.title in api_doc.parsed_classes:
                        endpoint_property.append(support_property.title)

                if isinstance(new_file[support_property.title], str):
                    if support_property.title in new_file:
                        member[support_property.title] = str(
                            new_file[support_property.title].replace(" ", ""))
                    else:
                        member[support_property.title] = "null"
            supported_properties_list = endpoint_property
            endpoint_property_list[endpoint] = property_list
            node_properties["class_property"] = str(
                supported_properties_list)
            # member is using for storing the fetched data in node.
            member["@id"] = str(new_file["@id"])
            member["@type"] = str(new_file["@type"])
            node_properties["property"] = str(member)
            class_object_node = self.addNode(
                "classes", str(endpoint), node_properties)
            self.addEdge(entrypoint_node, "has" + endpoint, class_object_node)
            # set edge between the entrypoint and the class endpoint/object
            if supported_properties_list:
                self.objects_property(
                    class_object_node,
                    supported_properties_list,
                    entrypoint_node,
                    api_doc)
        # for connect the nodes to endpoint which have endpoint as a property.
        if endpoint_property_list:
            for endpoint_property in endpoint_property_list:
                for src_node in self.redis_graph.nodes.values():
                    if str(endpoint_property) == src_node.alias:
                        for endpoints in endpoint_property_list[
                                               endpoint_property]:
                            for nodes in self.redis_graph.nodes.values():
                                if endpoints == nodes.alias:
                                    self.addEdge(
                                        src_node,
                                        "has_endpoint_property",
                                        nodes)
                                    break
                        break
