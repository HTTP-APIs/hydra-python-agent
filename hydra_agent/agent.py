import logging
from hydra_agent.redis_proxy import RedisProxy
from hydra_agent.graphutils_operations import GraphOperations
from hydra_agent.hydra_graph import InitialGraph
from hydra_python_core import doc_maker
from typing import Union, Tuple
from requests import Session

logger = logging.getLogger(__file__)


class Agent(Session):
    def __init__(self, entrypoint_url: str) -> None:
        self.entrypoint_url = entrypoint_url.strip().rstrip('/')
        self.redis_proxy = RedisProxy()
        self.redis_connection = self.redis_proxy.get_connection()
        self.graph_operations = GraphOperations(entrypoint_url,
                                                self.redis_proxy)
        super().__init__()
        jsonld_api_doc = super().get(self.entrypoint_url + '/vocab').json()
        self.api_doc = doc_maker.create_doc(jsonld_api_doc)
        self.initialize_graph()

    def initialize_graph(self) -> None:
        self.graph = InitialGraph()
        self.redis_connection.delete("apigraph")
        self.graph.main(self.entrypoint_url, self.api_doc, True)
        self.redis_connection.sadd("fs:url", self.entrypoint_url)

    def get(self, url: str) -> Union[dict, list]:
        response = self.graph_operations.get_resource(url)
        if response is not None:
            return response

        response = super().get(url)

        if response.status_code == 200:
            self.graph_operations.get_processing(url, response.json())

        return response.json()

    def put(self, url: str, new_object: dict) -> Tuple[dict, str]:
        response = super().put(url, json=new_object)

        if response.status_code == 201:
            url = response.headers['Location']
            self.graph_operations.put_processing(url, new_object)
            return response.json(), response.headers['Location']

        return response.json(), None

    def post(self, url: str, updated_object: dict) -> dict:
        response = super().post(url, json=updated_object)

        if response.status_code == 200:
            self.graph_operations.post_processing(url, updated_object)

        return response.json()

    def delete(self, url: str) -> dict:
        response = super().delete(url)

        if response.status_code == 200:
            self.graph_operations.delete_processing(url)

        return response.json()

if __name__ == "__main__":
    pass
