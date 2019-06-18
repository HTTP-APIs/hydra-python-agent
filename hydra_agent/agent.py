import logging
from redis_proxy import RedisProxy
from graphutils_operations import GraphOperations
from requests import Session

logger = logging.getLogger(__file__)


class HydraAgent(Session):
    def __init__(self, entrypoint_url):
        self.entrypoint_url = entrypoint_url
        self.redis_proxy = RedisProxy()
        self.graph_operations = GraphOperations(entrypoint_url,
                                                self.redis_proxy)
        super().__init__()

    def get(self, url):
        response = super().get(url)

        if response.status_code == 200:
            self.graph_operations.get_processing(url, response.json())

        return response

    def put(self, url, new_object):
        response = super().put(url, json=new_object)

        if response.status_code == 201:
            url = response.headers['Location']
            self.graph_operations.put_processing(url, new_object)

        return response

    def post(self, url, updated_object):
        response = super().post(url, json=updated_object)

        if response.status_code == 200:
            self.graph_operations.post_processing(url, updated_object)

        return response

    def delete(self, url):
        response = super().delete(url)

        if response.status_code == 200:
            self.graph_operations.delete_processing(url)

        return response

if __name__ == "__main__":
    HydraAgent = HydraAgent("http://localhost:8080/serverapi")

    new_object = {"@type": "Drone", "DroneState": "Simplified state",
                  "name": "Smart Drone", "model": "Hydra Drone",
                  "MaxSpeed": "999", "Sensor": "Wind"}

    logger.info(HydraAgent.get("http://localhost:8080/serverapi/DroneCollection/"))
    # logger.info(HydraAgent.put("http://localhost:8080/serverapi/DroneCollection/",
    #      new_object))
    # logger.info(HydraAgent.post("http://localhost:8080/serverapi/DroneCollection/fd1e4cc5-6223-4e8a-b544-6dc9b2e60cf7",
    #      new_object))
    # logger.info(HydraAgent.delete("http://localhost:8080/serverapi/DroneCollection/fd1e4cc5-6223-4e8a-b544-6dc9b2e60cf7"))
