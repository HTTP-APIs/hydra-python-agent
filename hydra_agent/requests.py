import urllib.request
import json
import logging
from urllib.error import URLError, HTTPError
from redis_proxy import RedisProxy
from graphutils import GraphUtils
from redisgraph import Graph, Node

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Requests:

    def __init__(self, entrypoint_url, redis_connection):
        self.entrypoint_url = entrypoint_url
        self.redis_connection = redis_connection
        self.connection = redis_connection.get_connection()
        self.vocabulary = 'vocab'
        self.graph_utils = GraphUtils(redis_connection)
        self.redis_graph = Graph("apidoc", redis_connection)

    def get(self, url):
        """Fetch data from the server and update Redis accordingly
        :param url: url for fetching the data.
        :return: loaded data.
        """
        # Issuing GET Request to Server
        try:
            response = urllib.request.urlopen(url)
        except HTTPError as e:
            logger.info('Request Error Code: ', e.code)
            return e
        except URLError as e:
            logger.info('Request Error Reason: ', e.reason)
            return e
        except ValueError as e:
            logger.info("Request Value Error:", e)
            return e
        else:
            json_response = json.loads(response.read().decode('utf-8'))

        if self.entrypoint_url in url:
            url = url.rstrip('/')
            url = url.replace(self.entrypoint_url, "EntryPoint")
        else:
            print("URL doesn't match with server URL")
            return "ERROR: URL doesn't match with server URL"

        # Updating Redis
        # First case - When processing a GET for a resource
        try:
            entrypoint, resource_endpoint, resource_id = url.split('/')

            # Building the the collection id, i.e. vocab:Entrypoint/Collection
            redis_resource_id = self.vocabulary + \
                ":" + entrypoint + \
                "/" + resource_endpoint

            collection_members = self.graph_utils.read(
                match="collection",
                where="id='{}'".format(redis_resource_id),
                ret="members")

            # Accessing the members with redis-set response structure
            # eval to parse it to a python list
            collection_members = eval(collection_members[0][1][0].decode())
            collection_members.append({'@id': json_response['@id'],
                                       '@type': json_response['@type']})

            self.graph_utils.update(
                match="collection",
                where="id='{}'".format(redis_resource_id),
                set="members = \"{}\"".format(str(collection_members)))
            return json_response
        except ValueError as e:
            # Second Case - When processing a GET for a Colletion
            try:
                entrypoint, resource_endpoint = url.split('/')
                redis_resource_id = self.vocabulary + \
                    ":" + entrypoint + \
                    "/" + resource_endpoint

                self.graph_utils.update(
                    match="collection",
                    where="id='{}'".format(redis_resource_id),
                    set="members = \"{}\"".format(str(json_response["members"])))
                return json_response

            # Third Case - When processing a valid GET that is not compatible
            # the Redis Structure built, only returns response
            except Exception as e:
                logger.info("No modification to Redis was made")
                return json_response

if __name__ == "__main__":
    requests = Requests("http://localhost:8080/serverapi",
                        RedisProxy())

    logger.info(requests.get("http://localhost:8080/serverapi/DroneCollection/"))
