from hydra_agent.requests import Requests
from hydra_agent.redis_proxy import RedisProxy
from hydra_agent.sync_mechanism import SynchronizationProcessing
from requests import Session


class HydraAgent(Session):
    def __init__(self, entrypoint_url):
        self.entrypoint_url = entrypoint_url
        self.redis_proxy = RedisProxy()
        self.sync_processing = SynchronizationProcessing(entrypoint_url,
                                                         self.redis_proxy)
        super().__init__()

    def get(self, url):
        response = super().get(url)
        self.sync_processing.add_operation("GET", url)

        return response

    def delete(self, url):
        response = super().delete(url)
        self.sync_processing.add_operation("DELETE", url)

        return response

if __name__ == "__main__":
    HydraAgent = HydraAgent("http://localhost:8080/serverapi")

    # print(HydraAgent.get("http://localhost:8080/serverapi/DroneCollection/"))
    print(HydraAgent.delete("http://localhost:8080/serverapi/DroneCollection/255e9a19-010d-4dab-ad9c-329316c20246"))
    