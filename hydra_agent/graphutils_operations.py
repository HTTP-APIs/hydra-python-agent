import urllib.request
import json
import logging
from urllib.error import URLError, HTTPError
from hydra_agent.redis_proxy import RedisProxy
from hydra_agent.graphutils import GraphUtils
from redisgraph import Graph, Node

logger = logging.getLogger(__file__)


class GraphOperations():

    def __init__(self, entrypoint_url, redis_proxy):
        self.entrypoint_url = entrypoint_url
        self.redis_proxy = redis_proxy
        self.redis_connection = redis_proxy.get_connection()
        self.vocabulary = 'vocab'
        self.graph_utils = GraphUtils(redis_proxy)
        self.redis_graph = Graph("apigraph", self.redis_connection)

    def get_processing(self, url: str, resource: dict) -> None:
        """Synchronize Redis upon new GET operations
        :param url: Resource URL to be updated in Redis.
        :param resource: Resource object fetched from server.
        :return: None.
        """
        url = url.rstrip('/').replace(self.entrypoint_url, "EntryPoint")
        url_list = url.split('/')
        # Updating Redis
        # First case - When processing a GET for a resource
        if len(url_list) == 3:
            entrypoint, resource_endpoint, resource_id = url.split('/')

            # Building the the collection id, i.e. vocab:Entrypoint/Collection
            redis_collection_id = self.vocabulary + \
                ":" + entrypoint + \
                "/" + resource_endpoint

            collection_members = self.graph_utils.read(
                match=":collection",
                where="id='{}'".format(redis_collection_id),
                ret=".members")

            # Checking if it's the first member to be loaded
            if collection_members is None:
                collection_members = []
            else:
                collection_members = eval(collection_members[0]['members'])

            collection_members.append({'@id': resource['@id'],
                                       '@type': resource['@type']})
            # Updating the collection properties with the nem member
            self.graph_utils.update(
                match="collection",
                where="id='{}'".format(redis_collection_id),
                set="members = \"{}\"".format(str(collection_members)))

            # Creating node for new collection member and commiting to Redis
            self.graph_utils.add_node("objects" + resource['@type'],
                                      resource['@type'] + resource_id,
                                      resource)
            self.graph_utils.commit()

            # Creating relation between collection node and member
            self.graph_utils.create_relation(label_source="collection",
                                             where_source="type : \'" +
                                             resource_endpoint + "\'",
                                             relation_type="has_" +
                                             resource['@type'],
                                             label_dest="objects" +
                                             resource['@type'],
                                             where_dest="id : \'" +
                                             resource['@id'] + "\'")
            return
        # Second Case - When processing a GET for a Collection
        elif len(url_list) == 2:
            entrypoint, resource_endpoint = url.split('/')
            redis_collection_id = self.vocabulary + \
                ":" + entrypoint + \
                "/" + resource_endpoint

            self.graph_utils.update(
                match="collection",
                where="id='{}'".format(redis_collection_id),
                set="members = \"{}\"".format(str(resource["members"])))
            return

        # Third Case - When processing a valid GET that is not compatible-
        # with the Redis Hydra structure, only returns response
        else:
            logger.info("No modification to Redis was made")
            return

    def put_processing(self, url, new_object) -> None:
        """Synchronize Redis upon new PUT operations
        :param url: URL for the resource to be created.
        :return: None.
        """
        # Manually add the id that will be on the server for the object added
        url_list = url.split('/', 3)
        new_object["@id"] = '/' + url_list[-1]
        # Simply call sync_get to add the resource to the collection at Redis
        self.get_processing(url, new_object)
        return

    def post_processing(self, url, updated_object) -> None:
        """Synchronize Redis upon new POST operations
        :param url: URL for the resource to be updated.
        :return: None.
        """
        # Manually add the id that will be on the server for the object added
        url_list = url.split('/', 3)
        updated_object["@id"] = '/' + url_list[-1]

        # Simply call sync_get to add the resource to the collection at Redis
        self.get_processing(url, updated_object)
        return

    def delete_processing(self, url) -> None:
        """Synchronize Redis upon new DELETE operations
        :param url: URL for the resource deleted.
        :return: None.
        """
        url = url.rstrip('/').replace(self.entrypoint_url, "EntryPoint")
        entrypoint, resource_endpoint, resource_id = url.split('/')

        # Building the the collection id, i.e. vocab:Entrypoint/Collection
        redis_collection_id = self.vocabulary + \
            ":" + entrypoint + \
            "/" + resource_endpoint

        collection_members = self.graph_utils.read(
            match=":collection",
            where="id='{}'".format(redis_collection_id),
            ret=".members")

        # Checking if it's the first member to be loaded
        if collection_members is None:
            return
        else:
            collection_members = eval(collection_members[0]['members'])

        for member in collection_members:
            if resource_id in member['@id']:
                collection_members.remove(member)

        self.graph_utils.update(
            match="collection",
            where="id='{}'".format(redis_collection_id),
            set="members = \"{}\"".format(str(collection_members)))
        return

    def get_resource(self, url: str) -> dict:
        """Get resources already stored on Redis and return
        :param url: URL for the resource to fetch.
        :return: Object with resource found.
        """
        # This is the first step to interact with Redis properly
        # This method should eventually accept a type, a id or an url 
        # do the proper checking and then return the cached info
        url_aux = url.rstrip('/').replace(self.entrypoint_url, "EntryPoint")
        url_list = url_aux.split('/')

        # Checking if querying for cached Collection or Member
        if len(url_list) == 2:
            entrypoint, resource_endpoint = url_aux.split('/')
            object_id = self.vocabulary + \
                ":" + entrypoint + \
                "/" + resource_endpoint
        else:
            url_list = url.split('/', 3)
            object_id = '/' + url_list[-1]

        resource = self.graph_utils.read(
                            match="",
                            where="id='{}'".format(object_id),
                            ret="")
        # If having only one object/querying by id return only dict
        if resource is not None and len(resource) == 1:
            return resource[0]

        return resource

if __name__ == "__main__":
    pass
