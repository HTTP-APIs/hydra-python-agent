import logging
import sys
import socketio
from hydra_agent.redis_core.redis_proxy import RedisProxy
from hydra_agent.redis_core.graphutils_operations import GraphOperations
from hydra_agent.redis_core.graph_init import InitialGraph
from hydra_python_core import doc_maker
from hydra_python_core.doc_writer import HydraDoc
from typing import Union, Tuple
from requests import Session
import json
from hydra_agent.helpers import expand_template
from hydra_agent.collection_paginator import Paginator
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)


class Agent(Session, socketio.ClientNamespace, socketio.Client):
    """Provides a straightforward GET, PUT, POST, DELETE -
    CRUD interface - to query hydrus
    """

    def __init__(self, entrypoint_url: str, namespace: str = '/sync') -> None:
        """Initialize the Agent
        :param entrypoint_url: Entrypoint URL for the hydrus server
        :param namespace: Namespace endpoint to listen for updates
        :return: None
        """
        self.entrypoint_url = entrypoint_url.strip().rstrip('/')
        self.redis_proxy = RedisProxy()
        self.redis_connection = self.redis_proxy.get_connection()
        Session.__init__(self)
        self.fetch_apidoc()
        self.initialize_graph()
        self.graph_operations = GraphOperations(self.entrypoint_url,
                                                self.api_doc,
                                                self.redis_proxy)
        # Declaring Socket Rules and instantiation Synchronization Socket
        socketio.ClientNamespace.__init__(self, namespace)
        socketio.Client.__init__(self, logger=True)
        socketio.Client.register_namespace(self, self)
        socketio.Client.connect(self, self.entrypoint_url,
                                namespaces=namespace)
        self.last_job_id = ""

    def fetch_apidoc(self) -> HydraDoc:
        """Fetches API DOC from Link Header by checking the hydra apiDoc
        relation and passes the obtained JSON-LD to doc_maker module of
        hydra_python_core to return HydraDoc which is used by the agent.
        :return HydraDoc created from doc_maker module
        """
        try:
            res = super().get(self.entrypoint_url)
            api_doc_url = res.links['http://www.w3.org/ns/hydra/core#apiDocumentation']['url']
            jsonld_api_doc = super().get(api_doc_url).json()
            self.api_doc = doc_maker.create_doc(jsonld_api_doc, self.entrypoint_url, 'serverapi')
            return self.api_doc
        except:
            print("Error parsing your API Documentation")
            raise

    def initialize_graph(self) -> None:
        """Initialize the Graph on Redis based on ApiDoc
        :param entrypoint_url: Entrypoint URL for the hydrus server
        :return: None
        """
        self.graph = InitialGraph()
        self.redis_connection.delete("apigraph")
        self.graph.main(self.entrypoint_url, self.api_doc, True)
        self.redis_connection.sadd("fs:url", self.entrypoint_url)

    def get(self, url: str = None, resource_type: str = None,
            follow_partial_links: bool = False,
            filters: dict = {},
            cached_limit: int = sys.maxsize) -> Union[dict, list, Paginator]:
        """READ Resource from Server/cached Redis
        :param url: Resource URL to be fetched
        :param resource_type: Resource object type
        :param filters: filters to apply when searching, resources properties
        :param cached_limit : Minimum amount of resources to be fetched
        :param follow_partial_links: If set to True, Paginator can go through pages.
        :return: Dict when one object or a list when multiple targeted objects
        :return: Iterator when param follow_partial_links is set to true
                    Iterator will be returned.
                    Usage:
                    paginator = agent.get('http://localhost:8080/serverapi/DroneCollection', \
                                        follow_partial_links=True)
                    To paginate forward:
                    ford = paginator.initialize_forward()
                    To get the members of first page:
                    next(ford)
                    To get the members of second page:
                    next(ford)
                    To paginate Backwards:
                    back = paginator.initialize_backward()
                    To get the members of prev page:
                    next(back)
                    To Jump:
                    paginator.jump_to_page(2) 
        """
        print("I am called", url)
        redis_response = self.graph_operations.get_resource(url, self.graph, resource_type,
                                                            filters)
        print("redis response", redis_response)
        if redis_response:
            if type(redis_response) is dict:
                return redis_response
            elif len(redis_response) >= cached_limit:
                return redis_response

        # If querying with resource type build url
        # This can be more stable when adding Manages Block
        # More on: https://www.hydra-cg.com/spec/latest/core/#manages-block
        if resource_type:
            url = self.entrypoint_url + "/" + resource_type + "Collection"
            response = super().get(url, params=filters)
        else:
            if not bool(filters):
                print("Getting resource")
                response = super().get(url)
                print("RESPONSE", response.json(), response.status_code)
            else:
                response_body = super().get(url)
                # filters can be simple dict or a json-ld
                templated_url = expand_template(
                    url, response_body.json(), filters)
                response = super().get(templated_url)

        if response.status_code == 200:
            # Graph_operations returns the embedded resources if finding any
            print("Again going for embedding resources", url)
            embedded_resources = \
                self.graph_operations.get_processing(url, response.json())
            self.process_embedded(embedded_resources)
            if response.json()['@type'] in self.api_doc.parsed_classes:
                return response.json()
            else:
                if follow_partial_links:
                    return Paginator(response=response.json())
                else:
                    return response.json()
        else:
            return response.text

    def put(self, url: str, new_object: dict) -> Tuple[dict, str]:
        """CREATE resource in the Server/cache it on Redis
        :param url: Server URL to create the resource at
        :param new_object: Dict containing the object to be created
        :return: Dict with server's response and resource URL
        """
        response = super().put(url, json=new_object)

        if response.status_code == 201:
            url = response.headers['Location']
            # Graph_operations returns the embedded resources if finding any
            full_resource = super().get(url)
            print("Going into put processing.....")
            embedded_resources = self.graph_operations.put_processing(url, full_resource.json())
            print("Now processing emvedded resources")
            self.process_embedded(embedded_resources)
            return response.json(), url
        else:
            return response.text, ""

    def post(self, url: str, updated_object: dict) -> dict:
        """UPDATE resource in the Server/cache it on Redis
        :param url: Server URL to update the resource at
        :param updated_object: Dict containing the updated object
        :return: Dict with server's response
        """
        response = super().post(url, json=updated_object)

        if response.status_code == 200:
            # Graph_operations returns the embedded resources if finding any
            print("Embedding resources")
            embedded_resources = \
                self.graph_operations.post_processing(url, updated_object)
            self.process_embedded(embedded_resources)
            return response.json()
        else:
            return response.text

    def delete(self, url: str) -> dict:
        """DELETE resource in the Server/delete it on Redis
        :param url: Resource URL to be deleted
        :return: Dict with server's response
        """
        response = super().delete(url)

        if response.status_code == 200:
            self.graph_operations.delete_processing(url)
            return response.json()
        else:
            return response.text

    def process_embedded(self, embedded_resources: list) -> None:
        """Helper function to process a list of embedded resources
        fetching and linking them to their parent Nodes
        :param embedded_resources: List of dicts containing resources
        """
        # Embedded resources are fetched and then properly linked
        for embedded_resource in embedded_resources:
            print("Getting embedded Resources")
            self.get(embedded_resource['embedded_url'])
            self.graph_operations.link_resources(
                embedded_resource['parent_id'],
                embedded_resource['parent_type'],
                embedded_resource['embedded_url'],
                embedded_resource['embedded_type'],
                self.graph)

    # Below are the functions that are responsible to process Socket Events
    def on_connect(self, data: dict = None) -> None:
        """Method executed when the Agent is successfully connected to the Server
        """
        if data:
            self.last_job_id = data['last_job_id']
            logger.info('Socket Connection Established - Synchronization ON')

    def on_disconnect(self):
        """Method executed when the Agent is disconnected
        """
        pass

    def on_update(self, data) -> None:
        """Method executed when the Agent receives an event named 'update'
        This is sent to all clients connected the server under the designed Namespace
        :param data: Dict object with the last inserted row of modification's table
        """
        row = data
        # Checking if the Client is the last job id is up to date with the Server
        if row['last_job_id'] == self.last_job_id:
            # Checking if it's an already cached resource, if not it will ignore
            if self.graph_operations.get_resource(row['resource_url']):
                if row['method'] == 'POST':
                    self.graph_operations.delete_processing(
                        row['resource_url'])
                    self.get(row['resource_url'])
                elif row['method'] == 'DELETE':
                    self.graph_operations.delete_processing(
                        row['resource_url'])
                if row['method'] == 'PUT':
                    pass
            # Updating the last job id
            self.last_job_id = row['job_id']

        # If last_job_id is not the same, there's more than one outdated modification
        # Therefore the Client will try to get the diff of all modifications after his last job
        else:
            super().emit('get_modification_table_diff',
                         {'agent_job_id': self.last_job_id})

        # Updating the last job id
        self.last_job_id = row['job_id']

    def on_modification_table_diff(self, data) -> None:
        """Event handler for when the client has to updated multiple rows
        :param data: List with all modification rows to be updated
        """
        new_rows = data
        # Syncing procedure for every row received by mod table diff
        for row in new_rows:
            if self.graph_operations.get_resource(row['resource_url']):
                if row['method'] == 'POST':
                    self.graph_operations.delete_processing(
                        row['resource_url'])
                    self.get(row['resource_url'])
                elif row['method'] == 'DELETE':
                    self.graph_operations.delete_processing(
                        row['resource_url'])
                if row['method'] == 'PUT':
                    pass

        # Checking if the Agent is too outdated and can't be synced
        if not new_rows:
            logger.info('Server Restarting - Automatic Sync not possible')
            self.initialize_graph()
            # Agent should reply with a connect event with the last_job_id
            super().emit('reconnect')
            return None

        # Updating the last job id
        self.last_job_id = new_rows[0]['job_id']

    def on_broadcast_event(self, data):
        """Method executed when the Agent receives a broadcast event
        :param data: Object with the data broadcasted
        """
        pass


if __name__ == "__main__":
    pass
