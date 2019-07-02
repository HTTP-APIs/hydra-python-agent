import logging
from redis_core.redis_proxy import RedisProxy
from redis_core.graphutils_operations import GraphOperations
from redis_core.graph_init import InitialGraph
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
        self.graph_operations = GraphOperations(entrypoint_url,
                                                self.redis_proxy)
        super().__init__()
        jsonld_api_doc = super().get(self.entrypoint_url + '/vocab').json()
        self.api_doc = doc_maker.create_doc(jsonld_api_doc)
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
            self.graph_operations.get_processing(url, response.json())

        return response.json()

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

        return response.json(), ""

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

    def delete(self, url: str) -> dict:
        """DELETE resource in the Server/delete it on Redis
        :param url: Resource URL to be deleted
        :return: Dict with server's response
        """
        response = super().delete(url)

        if response.status_code == 200:
            self.graph_operations.delete_processing(url)

        return response.json()

if __name__ == "__main__":
    # GRAPH.QUERY apigraph "MATCH (p:collection {id:'vocab:EntryPoint/DroneCollection'}) RETURN p.members"
    # GRAPH.QUERY apigraph "MATCH(p) WHERE(p.id='/serverapi/DroneCollection/d4a8106e-87ab-4f27-ad36-ecae3bca075c') RETURN p"
    agent = Agent("http://localhost:8080/serverapi")
    logger.info(agent.get("http://localhost:8080/serverapi/DroneCollection/"))
    #input(">>>")

    new_object = {"@type": "Drone", "DroneState": "Simplified state",
                  "name": "Smart Drone", "model": "Hydra Drone",
                  "MaxSpeed": "999", "Sensor": "Wind"}
    print("----PUT-----")
    response, new_resource_url = agent.put("http://localhost:8080/serverapi/DroneCollection/", new_object)
    print("----GET RESOURCE-----")
    logger.info(agent.get(new_resource_url))

    new_object["name"] = "Updated Name"
    del new_object["@id"]
    
    print("----POST-----")
    logger.info(agent.post(new_resource_url, new_object))

    print("----DELETE-----")
    logger.info(agent.delete(new_resource_url))

    print("----GET COLLECTION-----")
    logger.info(agent.get("http://localhost:8080/serverapi/DroneCollection/"))
    pass
