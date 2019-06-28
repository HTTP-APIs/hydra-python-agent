import urllib.request
import json
import re
import logging
from urllib.error import URLError, HTTPError
from hydra_agent.redis_core.classes_objects import ClassEndpoints, RequestError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CollectionEndpoints:
    """Contains all the collections endpoints and objects"""

    def __init__(self, redis_graph, class_endpoints):
        self.redis_graph = redis_graph
        self.class_endpoints = class_endpoints

    def fetch_data(self, new_url):
        """Fetching data from the server
        :param new_url: url for fetching the data.
        :return: loaded data.
        """
        try:
            response = urllib.request.urlopen(new_url)
        except HTTPError as e:
            logger.info('Error code: ', e.code)
            return RequestError("error")
        except URLError as e:
            logger.info('Reason: ', e.reason)
            return RequestError("error")
        except ValueError as e:
            logger.info("value error:", e)
            return RequestError("error")
        else:
            return json.loads(response.read().decode('utf-8'))

    def faceted_key(self, fs, key, value):
        return ("{}".format(fs + ":" + key + ":" + value))

    def faceted_indexing(self, key, redis_connection, member):
        for keys in member:
            redis_connection.sadd(
                self.faceted_key(
                    "fs", keys, member[keys]), key)

    def collectionobjects(
            self,
            endpoint_collection_node,
            endpoint_list,
            new_url,
            api_doc,
            url,
            redis_connection):
        """Creating nodes for all objects stored in collection.
        :param endpoint_collection_node: parent/collection endpoint node.
        :param endpoint_list: Members/objects of any collection.
        :param new_url: parent url for members/objects
        :param api_doc: Apidocumentation for particular url.
        :param url: Base url given by user.
        :param redis_connection: connection of Redis memory.
        """
        print("accesing the collection object like events or drones")
        if endpoint_list:
            clas = ClassEndpoints(self.redis_graph, self.class_endpoints)
            for endpoint in endpoint_list:
                node_properties = {}
                no_endpoint_list = []
                endpoint_method = []
                member = {}
                endpoint_property_list = []
                supported_property_list = []
                no_endpoint_property = {}
                match_obj = re.match(
                    r'/(.*)/(.*)/(.*)?', endpoint["@id"], re.M | re.I)
                base_url = "/{0}/{1}/".format(match_obj.group(1),
                                              match_obj.group(2))
                entrypoint_member = endpoint["@type"].lower(
                ) + match_obj.group(3)
#                print(base_url, entrypoint_member,endpoint["@type"])
                member_alias = entrypoint_member
                # key for the object node is memeber_alias
                member_id = match_obj.group(3)
                member_url = new_url + "/" + member_id
                # object data retrieving from the server
                new_file = self.fetch_data(member_url)
                if isinstance(new_file, RequestError):
                    return None
                for support_operation in api_doc.parsed_classes[
                    endpoint["@type"]
                ]["class"
                  ].supportedOperation:
                    endpoint_method.append(support_operation.method)
                # all the operations for the object is stored in method
                node_properties["operations"] = str(endpoint_method)
                # endpoint_property_list store all properties which-
                # is class/object and also an endpoint.
                # supported_property_list store all the properties.
                # no_endpoint_list store all properties which is class/object
                # but not endpoint.
                for support_property in api_doc.parsed_classes[
                    endpoint["@type"]
                ]["class"
                  ].supportedProperty:
                    supported_property_list.append(support_property.title)
                    if support_property.title in self.class_endpoints:
                        endpoint_property_list.append(
                            str(support_property.title))
                    elif support_property.title in api_doc.parsed_classes:
                        no_endpoint_list.append(support_property.title)

                    # members contain all the property with value.
                    # it contains null value for the property which-
                    #  not have value in server.
                    # no_endpoint_properrty store value for no_endpoint_list.
                    if support_property.title in new_file:
                        if isinstance(new_file[support_property.title], str):
                            member[support_property.title] = str(
                                new_file[
                                    support_property.title].replace(" ", ""))
                        else:
                            no_endpoint_property[
                                support_property.title] = new_file[
                                support_property.title]
                    else:
                        member[support_property.title] = "null"

                node_properties["@id"] = str(endpoint["@id"])
                node_properties["@type"] = str(endpoint["@type"])
                member[endpoint["@type"]] = str(endpoint["@id"])
                node_properties["property_value"] = str(member)
                member["type"] = str(endpoint["@type"])
                self.faceted_indexing(
                    endpoint["@id"], redis_connection, member)
                node_properties["properties"] = str(supported_property_list)
                # add object as a node in redis
                collection_object_node = clas.addNode(
                    str("objects" + str(endpoint["@type"])),
                    str(member_alias.capitalize()),
                    node_properties)
                print(collection_object_node)
                # set an edge between the collection and its object
                clas.addEdge(endpoint_collection_node,
                             "has_" + str(endpoint["@type"]),
                             collection_object_node)

                if endpoint_property_list:
                    for endpoint_property in endpoint_property_list:
                        for nodes in self.redis_graph.nodes.values():
                            if endpoint_property == nodes.alias:
                                clas.addEdge(
                                    collection_object_node,
                                    "hasendpointproperty",
                                    nodes)
                if no_endpoint_list:
                    clas.objects_property(
                        collection_object_node,
                        no_endpoint_list,
                        no_endpoint_property,
                        api_doc)

        else:
            print("NO MEMBERS")

    def load_from_server(
            self,
            endpoint,
            api_doc,
            url,
            redis_connection):
        """Load data or members from collection endpoint
        :param endpoint: Given endpoint for load data from server.
        :param api_doc: Apidocumentation for particular url.
        :param url: Base url given by user.
        :param redis_connection: connection to Redis memory.
        """
        print(
            "check url for endpoint",
            url + "/" +
            endpoint)
        new_url = url + "/" + endpoint
        # url for every collection endpoint
        new_file = self.fetch_data(new_url)
        if isinstance(new_file, RequestError):
            return None
        # retrieving the objects from the collection endpoint
        for node in self.redis_graph.nodes.values():
            if node.alias == endpoint:
                node.properties["members"] = str(new_file["members"])
                # update the properties of node by its members
                endpoint_collection_node = node

        self.collectionobjects(
            endpoint_collection_node,
            new_file["members"],
            new_url,
            api_doc,
            url,
            redis_connection
        )
        # delete all the old data that has saved in Redis using redis_graph.
        # It will remove duplicate data from Redis.
        for key in redis_connection.keys():
            if "fs:" not in key.decode("utf8"):
                redis_connection.delete(key)
        # save the new data.
        self.redis_graph.commit()
#        for node in self.redis_graph.nodes.values():
#            print("\n",node.alias)

    def endpointCollection(
            self,
            collection_endpoint,
            entrypoint_node,
            api_doc,
            url):
        """It makes a node for every collection endpoint."""
        print("accessing every collection in entrypoint")
        clas = ClassEndpoints(self.redis_graph, self.class_endpoints)
        for endpoint in collection_endpoint:
            endpoint_method = []
            node_properties = {}
            for support_operation in api_doc.collections[
                    endpoint][
                    "collection"].supportedOperation:
                endpoint_method.append(support_operation.method)
            node_properties["operations"] = str(endpoint_method)
            # all the operations for the collection endpoint is stored in
#            print("supportedOperations",node_properties["operations"])
            node_properties["@id"] = str(collection_endpoint[endpoint])
            node_properties["@type"] = str(endpoint)
            endpoint_collection_node = clas.addNode(
                "collection", endpoint, node_properties)
#            print(endpoint_collection_node)
            clas.addEdge(
                entrypoint_node,
                "has_collection",
                endpoint_collection_node)
            # set an edge between the entrypoint and collection endpoint
