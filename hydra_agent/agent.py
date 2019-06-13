from redis_proxy import RedisProxy
from sync_mechanism import SynchronizationProcessing
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

        if response.status_code == 200:
            self.sync_processing.add_operation("GET", url)

        return response

    def put(self, url, new_object):
        response = super().put(url, json=new_object)

        if response.status_code == 201:
            url = response.headers['Location']
            self.sync_processing.add_operation("PUT", url)

        return response

    def post(self, url, updated_object):
        response = super().post(url, json=updated_object)

        if response.status_code == 200:
            self.sync_processing.add_operation("POST", url)

        return response

    def delete(self, url):
        response = super().delete(url)

        if response.status_code == 200:
            self.sync_processing.add_operation("DELETE", url)

        return response

if __name__ == "__main__":
    HydraAgent = HydraAgent("http://localhost:8080/serverapi")

    new_object = {"@type": "Drone", "DroneState": "Simplified state",
                  "name": "Smart Drone", "model": "Hydra Drone",
                  "MaxSpeed": "999", "Sensor": "Wind"}

    print(HydraAgent.get("http://localhost:8080/serverapi/DroneCollection/"))
    # print(HydraAgent.put("http://localhost:8080/serverapi/DroneCollection/",
    #      new_object))
    # print(HydraAgent.post("http://localhost:8080/serverapi/DroneCollection/ec86b237-d75d-4911-9220-8e02ea4ef860",
    #      new_object))
    # print(HydraAgent.delete("http://localhost:8080/serverapi/DroneCollection/255e9a19-010d-4dab-ad9c-329316c20246"))
