import logging
from hydra_agent.redis_core.redis_proxy import RedisProxy
from hydra_agent.redis_core.graphutils_operations import GraphOperations
from hydra_agent.redis_core.graph_init import InitialGraph
from hydra_python_core import doc_maker
from typing import Union, Tuple
from requests import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)


class Agent(Session):
    def __init__(self, entrypoint_url: str) -> None:
        """Initialize the Agent
        :param entrypoint_url: Entrypoint URL for the hydrus server
        :return: None
        """
        self.entrypoint_url = entrypoint_url.strip().rstrip('/')
        self.redis_proxy = RedisProxy()
        self.redis_connection = self.redis_proxy.get_connection()
        super().__init__()
        jsonld_api_doc = super().get(self.entrypoint_url + '/vocab').json()
        self.api_doc = doc_maker.create_doc(jsonld_api_doc)
        self.graph_operations = GraphOperations(entrypoint_url,
                                                self.api_doc,
                                                self.redis_proxy)
        self.initialize_graph()

    def initialize_graph(self) -> None:
        """Initialize the Graph on Redis based on ApiDoc
        :param entrypoint_url: Entrypoint URL for the hydrus server
        :return: None
        """
        self.graph = InitialGraph()
        self.redis_connection.delete("apigraph")
        self.graph.main(self.entrypoint_url, self.api_doc, True)
        self.redis_connection.sadd("fs:url", self.entrypoint_url)

    def get(self, url: str) -> Union[dict, list]:
        """READ Resource from Server/cached Redis
        :param url: Resource URL to be fetched
        :return: Dict when one object or a list when multiple targerted objects
        """
        response = self.graph_operations.get_resource(url)
        if response is not None:
            return response

        response = super().get(url)

        if response.status_code == 200:
            # Graph operations returns embedded resources if finding any
            embedded_resources = \
                self.graph_operations.get_processing(url, response.json())
            # Embedded resources are fetched and then properly linked
            for embedded_resource in embedded_resources:
                self.get(embedded_resource['embedded_url'])
                self.graph_operations.embedded_resource(
                    embedded_resource['parent_id'],
                    embedded_resource['parent_type'],
                    embedded_resource['embedded_url']
                )
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
            self.graph_operations.put_processing(url, new_object)
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
            self.graph_operations.post_processing(url, updated_object)
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
        

if __name__ == "__main__":
    pass