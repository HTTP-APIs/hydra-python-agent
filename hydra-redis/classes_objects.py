import urllib.request
import json
from redisgraph import Node, Edge


class ClassEndpoints:
    """Contains all the classes endpoint and the objects"""

    def __init__(self, redis_graph,class_endpoints):
        self.redis_graph = redis_graph
        self.class_endpoints = class_endpoints

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
            no_endpoint_property,
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
            node_properties["property_value"] = str(no_endpoint_property)
            node_alias = str(objects_node.alias + str(obj)).lower()
            # key for the node of the object
            node_properties["parent_id"] = str(objects_node.properties["@id"])
            object_node = self.addNode("object", node_alias, node_properties)
            self.addEdge(objects_node, "has" + str(obj), object_node)
            # set edge between the object and its parent object
            if endpoint_prop:
                self.objects_property(
                    object_node, endpoint_prop, api_doc)

    def load_from_server(
            base_url,
            class_endpoint_id,
            api_doc,
            ):
        """Loads data from class endpoints like its properties values"""
        print("check endpoint url....loading data")
        members ={}
        endpoint_property= []
        new_url = base_url + \
            class_endpoint_id
        # url for the classes endpoint
        print(new_url)
        response = urllib.request.urlopen(new_url)
        new_file = json.loads(response.read().decode('utf-8'))
        #retreiving data for the classes endpoint from server
        for support_property in api_doc.parsed_classes[
                                                   endpoint][
                                                   "class"].supportedProperty:
            if endpoint != support_property.title and support_property.title not in self.class_endpoints:
                if support_property.title in api_doc.parsed_classes:
                    endpoint_property.append(support_property.title)

            if support_property.title in new_file:
                if isinstance(new_file[support_property.title], str):
                    member[support_property.title] = str(
                        new_file[support_property.title].replace(" ", ""))
                else:
                    no_endpoint_property=new_file[support_property.title]
            else:
                member[support_property.title] = "null"
        for node in self.redis_graph.nodes.values():
            if node.alias == endpoint:
                node.properties["property_value"]= str(member)
                #update the properties of the node
                self.redis_graph.commit()
                class_object_node = node
                print (class_object_node)
        # set edge between the entrypoint and the class endpoint/object
        if endpoint_property:
            self.objects_property(
                class_object_node,
                endpoint_property,
                no_endpoint_property,
                api_doc)


    def endpointclasses(
            self,
            entrypoint_node,
            api_doc,
            base_url):
        """Node for every class which have an endpoint."""
        print("classes endpoint or accessing classes")
        endpoint_property_list = {}
        # contain all endpoints which have other endpoints as a property.
        for endpoint in self.class_endpoints:
            supported_properties_list=[]
            node_properties = {}
            # node_properties is used for set the properties of node.
            property_list = []
            node_properties["operations"] = self.get_operation(
                api_doc, endpoint)
            # store the operations for the endpoint

            for support_property in api_doc.parsed_classes[
                                                   endpoint][
                                                   "class"].supportedProperty:
                supported_properties_list.append(support_property.title)
                if endpoint != support_property.title:
                    if support_property.title in self.class_endpoints:
                        property_list.append(support_property.title)

            endpoint_property_list[endpoint] = property_list
            node_properties["@id"] = str(self.class_endpoints[endpoint])
            node_properties["@type"] = str(endpoint)
            node_properties["properties"]= str(supported_properties_list)
            class_object_node = self.addNode(
                "classes", str(endpoint), node_properties)
            print(class_object_node)
            self.addEdge(entrypoint_node, "has" + endpoint, class_object_node)
            # set edge between the entrypoint and the class endpoint/object
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
