import urllib.request
import json
import logging
from urllib.error import URLError, HTTPError
from redis_proxy import RedisProxy
from graphutils import GraphUtils
from redisgraph import Graph, Node
from requests import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SynchronizationProcessing(Session):

    def __init__(self, entrypoint_url, redis_connection):
        self.entrypoint_url = entrypoint_url
        self.redis_connection = redis_connection
        self.connection = redis_connection.get_connection()
        self.vocabulary = 'vocab'
        self.graph_utils = GraphUtils(redis_connection)
        self.redis_graph = Graph("apidoc", redis_connection)
        super().__init__()

    def sync_get(self, url):
        """Synchronize Redis upon new GET operations
        :param url: URL for to updated in Redis.
        :return: None.
        """
        # Receiving updated object from the Server
        json_response = super().get(url).json()

        url = url.rstrip('/').replace(self.entrypoint_url, "EntryPoint")
        # Updating Redis
        # First case - When processing a GET for a resource
        try:
            entrypoint, resource_endpoint, resource_id = url.split('/')

            # Building the the collection id, i.e. vocab:Entrypoint/Collection
            redis_collection_id = self.vocabulary + \
                ":" + entrypoint + \
                "/" + resource_endpoint

            collection_members = self.graph_utils.read(
                match="collection",
                where="id='{}'".format(redis_collection_id),
                ret="members")

            # Accessing the members with redis-set response structure
            collection_members = eval(collection_members[0][1][0].decode())
            collection_members.append({'@id': json_response['@id'],
                                       '@type': json_response['@type']})

            self.graph_utils.update(
                match="collection",
                where="id='{}'".format(redis_collection_id),
                set="members = \"{}\"".format(str(collection_members)))
            return
        except ValueError as e:
            # Second Case - When processing a GET for a Colletion
            try:
                entrypoint, resource_endpoint = url.split('/')
                redis_collection_id = self.vocabulary + \
                    ":" + entrypoint + \
                    "/" + resource_endpoint

                self.graph_utils.update(
                    match="collection",
                    where="id='{}'".format(redis_collection_id),
                    set="members = \"{}\"".format(str(json_response["members"])))
                return

            # Third Case - When processing a valid GET that is not compatible-
            # with the Redis Hydra structure, only returns response
            except Exception as e:
                logger.info("No modification to Redis was made")
                return

    def sync_delete(self, url):
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
            match="collection",
            where="id='{}'".format(redis_collection_id),
            ret="members")

        # Accessing the members with redis-set response structure and deleting
        collection_members = eval(collection_members[0][1][0].decode())
        for member in collection_members:
            if resource_id in member['@id']:
                collection_members.remove(member)

        self.graph_utils.update(
            match="collection",
            where="id='{}'".format(redis_collection_id),
            set="members = \"{}\"".format(str(collection_members)))
        return

    def add_operation(self, method, url):
        """Add operation to the Modifications Table at the server
        and also calls the respective method to synchronize Redis
        :param operation: Method that was sent to the server.
        :param url: URL for the resource modified.
        :return: None.
        """
        # [To be implemented] Should send here the new operation-
        # to the server modifications table
        
        if method == "GET":
            self.sync_get(url)

        if method == "DELETE":
            self.sync_delete(url)

if __name__ == "__main__":
    requests = Requests("http://localhost:8080/serverapi",
                        RedisProxy())

    logger.info(requests.get("http://localhost:8080/serverapi/DroneCollection/"))
