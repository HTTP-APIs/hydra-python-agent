import json
import logging
import urllib.request
from redisgraph import Edge
from urllib.error import URLError, HTTPError
from core.utils.graph_functions import GraphFunctions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RequestError(Exception):
    """A class for client-side exceptions"""
    pass


class ClassEndpoints:
    """Contains all the classes endpoint and the objects"""

    def __init__(self, redis_graph, class_endpoints, api_doc):
        self.class_endpoints = class_endpoints
        self.redis_graph = redis_graph
        self.api_doc = api_doc
        self.graph_funcs = GraphFunctions(self.redis_graph, self.api_doc)

    def addEdge(self, subject_node, predicate, object_node):
        """Add edge between 2 nodes in the redis graph.

        Args:
            subject_node: Subject of the new triple.
            predicate: Predicate of the new triple.
            object_node: Object of the new triple.
        """
        edge = Edge(subject_node, predicate, object_node)
        try:
            self.redis_graph.add_edge(edge)
        except Exception as err:
            raise err

    def get_operation(self, endpoint):
        """
        Return all the supportedOperations for given endpoint.

        Args:
            api_doc: API Documentaion for particular url.
            endpoint: Particular endpoint for getting
            supportedOperations.

        Returns:
            List of supportedOperations.
        """
        endpoint_operations = []

        for support_operation in self.api_doc.parsed_classes[
                endpoint][
                "class"].supportedOperation:
            endpoint_operations.append(support_operation.method)

        return str(endpoint_operations)

    def objects_property(
            self,
            objects_node,
            new_list,
            no_endpoint_property,
            api_doc):
        """
        Nodes for every that property which is itself an object.

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
            object_node = self.graph_funcs.addNode(
                str("object" + str(objects_node.properties["@type"])),
                node_alias,
                node_properties)
            self.graph_funcs.addEdge(objects_node, "has" + str(obj), object_node)
            # set edge between the object and its parent object
            if endpoint_prop:
                self.objects_property(
                    object_node, properties_title, endpoint_prop, api_doc)

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
            logger.error('Error code: {}'.format(e.code))
            return None
        except URLError as e:
            logger.error('Reason: {}'.format(e.reason))
            return None
        except ValueError as e:
            logger.info("Value Error: {}".format(e))
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

    def connect_nodes(self, endpoint_properties, node_alias):
        for class_endpoint in endpoint_properties:
            src_node = node_alias.get(class_endpoint)
            for endpoint in endpoint_properties[class_endpoint]:
                node = node_alias.get(endpoint)
                self.graph_funcs.addEdge(src_node, 'has_endpoint_property', node)

    def create_endpoint_nodes(
            self,
            entrypoint_node,
            base_url):
        """Creates a node for each classEndpoint.

        Args:
            entrypoint_node: Entrypoint Node or Parent Node.
            api_doc: Api Documentation for particular URL.
            base_url: Parent URL for accessing server.
        """
        # classEndpoints with other classEndpoints as properties
        node_alias = {}
        endpoint_properties = {}
        for endpoint in self.class_endpoints:
            # list of properties supported by the classEndpoint
            supported_properties = []
            property_list = []
            for endpoint_prop in self.api_doc.parsed_classes[
                    endpoint][
                    "class"].supportedProperty:
                supported_properties.append(endpoint_prop.title)
                # search for properties which are also classEndpoints
                # if endpoint != endpoint_prop.title:
                if endpoint_prop.title in self.class_endpoints:
                    property_list.append(endpoint_prop.title)

            # node_properties contains data to store in particular node.
            node_properties = {}
            node_properties["operations"] = self.get_operation(endpoint)
            node_properties["@id"] = str(self.class_endpoints[endpoint])
            node_properties["@type"] = str(endpoint)
            node_properties["properties"] = str(supported_properties)
            class_object_node = self.graph_funcs.addNode(
                "classes", str(endpoint), node_properties)
            # set edge between the entrypoint and the class endpoint.
            node_alias[str(endpoint)] = class_object_node
            self.graph_funcs.addEdge(entrypoint_node, "has" + endpoint, class_object_node)
            # add property_list to the endpoint_properties for corresponding endpoint
            endpoint_properties[endpoint] = property_list
        self.connect_nodes(endpoint_properties, node_alias)
