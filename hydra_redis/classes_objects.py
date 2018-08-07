import urllib.request
import json
import logging
from redisgraph import Node, Edge
from urllib.error import URLError, HTTPError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RequestError(Exception):
    """A class for client-side exceptions"""
    pass

class ClassEndpoints:
    """Contains all the classes endpoint and the objects"""

    def __init__(self, redis_graph, class_endpoints):
        self.redis_graph = redis_graph
        self.class_endpoints = class_endpoints

    def addNode(self, label1, alias1, properties1):
        """
        Add node to the redis graph
        :param label1: label for the node.
        :param alias1: alias for the node.
        :param properties: properties for the node.
        :return: Created Node
        """
        node = Node(label=label1, alias=alias1, properties=properties1)
        self.redis_graph.add_node(node)
        return node

    def addEdge(self, source_node, predicate, dest_node):
        """Add edge between nodes in redis graph
        :param source_node: source node of the edge.
        :param predicate: relationship between the source and destination node
        :param dest_node: destination node of the edge.
        """
        edge = Edge(source_node, predicate, dest_node)
        self.redis_graph.add_edge(edge)

    def get_operation(self, api_doc, endpoint):
        """Return all the supportedOperations for given endpoint
        :param api_doc: Apidocumentaion for particular url.
        :param endpoint: particular endpoint for getting supportedOperations.
        :return: All operations for endpoint.
        """
        endpoint_method = []

        for support_operation in api_doc.parsed_classes[
                endpoint][
                "class"].supportedOperation:
            endpoint_method.append(support_operation.method)
#        print("supportedOperation", endpoint_method)
        # all the operations for the object is stored in endpoint_method

        return str(endpoint_method)

    def objects_property(
            self,
            objects_node,
            new_list,
            no_endpoint_property,
            api_doc):
        """Nodes for every that property which is itself an object
        :param objects_node: particular member or class node(parent node).
        :param new_list: list of object properties.
        :param no_endpoint_property: property_value for new_list properties.
        :param api_doc: Apidocumentation of particular url.
        """
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
            node_properties["properties"] = str(properties_title)
            node_properties["property_value"] = str(no_endpoint_property[obj])
            node_alias = str(objects_node.alias + str(obj)).lower()
            # key for the node of the object
            node_properties["parent_id"] = str(objects_node.properties["@id"])
            object_node = self.addNode(
                str("object" + str(objects_node.properties["@type"])),
                node_alias,
                node_properties)
            self.addEdge(objects_node, "has" + str(obj), object_node)
            # set edge between the object and its parent object
            if endpoint_prop:
                self.objects_property(
                    object_node, endpoint_prop, api_doc)

    def faceted_key(self, key, value):
        return ("{}".format("fs:" + key + ":" + value))

    def faceted_indexing(self,
                         key,
                         redis_connection,
                         member):
        for keys in member:
            redis_connection.sadd(self.faceted_key(keys, member[keys]), key)

    def load_from_server(
            self,
            endpoint,
            api_doc,
            base_url,
            redis_connection):
        """Loads data from class endpoints like its properties values
        :param endpoint: Particular endpoint for load data from server.
        :param api_doc: Apidocumentation for particular url.
        :param base_url: Parent url for accessing server.
        :param redis_connection: connection for the Redis memory.
        """
        print("check endpoint url....loading data")
        member = {}
        endpoint_property = []
        no_endpoint_property = {}
        # new_url is url for the classes endpoint
        new_url = base_url + "/" + endpoint
        # retreiving data for the classes endpoint from server
        try:
            response = urllib.request.urlopen(new_url)
        except HTTPError as e:
            logger.info('Error code: ', e.code)
            return None
        except URLError as e:
            logger.info('Reason: ', e.reason)
            return None
        except ValueError as e:
            logger.info("value error:", e)
            return None
        else:
            new_file = json.loads(response.read().decode('utf-8'))
        # endpoint_property store all properties which is class/object but not
        # endpoint.
        for support_property in api_doc.parsed_classes[
                endpoint][
                "class"].supportedProperty:
            if (endpoint != support_property.title and
                    support_property.title not in self.class_endpoints):
                if support_property.title in api_doc.parsed_classes:
                    endpoint_property.append(support_property.title)

            # members store the properties with its value
            # members contains null if supportedProperty has no value in server
            # no_endpoint_property store object value of property
            # ex: values of state property.
            if support_property.title in new_file:
                if isinstance(new_file[support_property.title], str):
                    member[support_property.title] = str(
                        new_file[support_property.title].replace(" ", ""))
                else:
                    no_endpoint_property[support_property.title] = new_file[
                        support_property.title]
            else:
                member[support_property.title] = "null"
        # Add the property_value in endpoint node properties.
        for node in self.redis_graph.nodes.values():
            if node.alias == endpoint:
                # update the properties of the node
                node.properties["property_value"] = str(member)
                # Use faceted index to handle with comparison in properties.
                redis_connection.set((endpoint), member)
                self.faceted_indexing(endpoint, redis_connection, member)
                class_object_node = node
                print(class_object_node)
        # For creating relationship with endpoint_property elements.
        if endpoint_property:
            self.objects_property(
                class_object_node,
                endpoint_property,
                no_endpoint_property,
                api_doc)
        # delete all the old data that has saved in Redis using redis_graph.
        # It will remove duplicate data from Redis.
        for key in redis_connection.keys():
            if "fs:" not in key.decode("utf8"):
                redis_connection.delete(key)
        # save the new data.
        self.redis_graph.commit()

    def endpointclasses(
            self,
            entrypoint_node,
            api_doc,
            base_url):
        """Node for every class which have an endpoint.
        :param entrypoint_node: Endtrypoint or parent node.
        :param api_doc: Apidocumentation for particular url.
        :param base_url: parent url for accessing server.
        """
        print("classes endpoint or accessing classes")
        endpoint_property_list = {}
        # endpoint_property_list contain all endpoints
        # which have other endpoints as a property ex: State.
        for endpoint in self.class_endpoints:
            supported_properties_list = []
            # node_properties is used for set the properties of node.
            node_properties = {}
            property_list = []
            # store the operations for the endpoint
            node_properties["operations"] = self.get_operation(
                api_doc, endpoint)
            # supported_property_list contain all the properties of endpoint.
            # property list store the properties which is endpoint as well.
            for support_property in api_doc.parsed_classes[
                    endpoint][
                    "class"].supportedProperty:
                supported_properties_list.append(support_property.title)
                # findout the properties which is also an endpoint.
                if endpoint != support_property.title:
                    if support_property.title in self.class_endpoints:
                        property_list.append(support_property.title)

            endpoint_property_list[endpoint] = property_list
            # node_properties contains data to store in particular node.
            node_properties["@id"] = str(self.class_endpoints[endpoint])
            node_properties["@type"] = str(endpoint)
            node_properties["properties"] = str(supported_properties_list)
            class_object_node = self.addNode(
                "classes", str(endpoint), node_properties)
            # set edge between the entrypoint and the class endpoint.
            self.addEdge(entrypoint_node, "has" + endpoint, class_object_node)

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
