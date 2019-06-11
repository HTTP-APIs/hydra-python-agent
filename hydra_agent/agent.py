from hydra_agent.requests import Requests
from redis_proxy import RedisProxy


class HydraAgent(Requests):

    def get(self, url):
        # Some of the other coming "smart features" should be implemented here
        return super().get(url)

if __name__ == "__main__":
    HydraAgent = HydraAgent("http://localhost:8080/serverapi",
                            RedisProxy())

    print(HydraAgent.get("http://localhost:8080/serverapi/DroneCollection/"))
    