import unittest
from unittest.mock import patch, MagicMock, call
from hydra_agent.agent import Agent
from hydra_agent.redis_core.graphutils_operations import GraphOperations
from hydra_agent.tests.test_examples.hydra_doc_sample import doc as drone_doc


class TestAgent(unittest.TestCase):
    """
    TestCase for Agent Class
    """

    @patch('hydra_agent.agent.Session.get')
    def setUp(self, get_session_mock):
        """Setting up Agent object
        :param get_session_mock: MagicMock object for patching session.get
                                 it's used to Mock Hydrus response to ApiDoc
        """
        # Mocking get for ApiDoc to Server, so hydrus doesn't need to be up
        get_session_mock.return_value.json.return_value = drone_doc

        self.agent = Agent("http://localhost:8080/api")

    @patch('hydra_agent.agent.Session.get')
    def test_get_url(self, get_session_mock):
        """Tests get method from the Agent
        :param get_session_mock: MagicMock object for patching session.get
        """
        state_object = {"@id": "/api/StateCollection/1", "@type": "State",
                        "Battery": "sensor Ex", "Direction": "speed Ex",
                        "DroneID": "sensor Ex", "Position": "model Ex",
                        "SensorStatus": "sensor Ex", "Speed": "2",
                        "@context": "/api/contexts/StateCollection.jsonld"}

        get_session_mock.return_value.status_code = 200
        get_session_mock.return_value.json.return_value = state_object
        response = self.agent.get("http://localhost:8080/api/" +
                                  "StateCollection/1")

        self.assertEqual(response, state_object)

    @patch('hydra_agent.agent.Session.get')
    def test_get_class_properties(self, get_session_mock):
        """Tests get method from the Agent
        :param get_session_mock: MagicMock object for patching session.get
        """
        state_object = {"@id": "/api/StateCollection/1", "@type": "State",
                        "Battery": "sensor Ex", "Direction": "North",
                        "DroneID": "sensor Ex", "Position": "model Ex",
                        "SensorStatus": "sensor Ex", "Speed": "2",
                        "@context": "/api/contexts/StateCollection.jsonld",}

        get_session_mock.return_value.status_code = 200
        get_session_mock.return_value.json.return_value = state_object
        response_url = self.agent.get("http://localhost:8080/api/" + \
                                      "StateCollection/1")

        responses_graph = self.agent.get(resource_type="State",
                                         filters={"Direction": "North"},
                                         cached_limit=1)
        responses_graph = responses_graph[0]
        self.assertEqual(response_url, responses_graph)

    @patch('hydra_agent.agent.Session.get')
    @patch('hydra_agent.agent.Session.put')
    def test_get_collection(self, put_session_mock, embedded_get_mock):
        """Tests get method from the Agent
        :param get_processing_mock: MagicMock object to patch graphoperations
        :param get_mock: MagicMock object for patching session.get
        """
        new_object = {"@type": "Drone", "DroneState": "/api/StateCollection/1",
                      "name": "Smart Drone", "model": "Hydra Drone",
                      "MaxSpeed": "999", "Sensor": "Wind"}

        collection_url = "http://localhost:8080/api/DroneCollection/"
        new_object_url = collection_url + "1"

        put_session_mock.return_value.status_code = 201
        put_session_mock.return_value.json.return_value = new_object
        put_session_mock.return_value.headers = {'Location': new_object_url}

        state_object = {"@context": "/api/contexts/StateCollection.jsonld",
                        "@id": "/api/StateCollection/1", "@type": "State",
                        "Battery": "sensor Ex", "Direction": "speed Ex",
                        "DroneID": "sensor Ex", "Position": "model Ex",
                        "SensorStatus": "sensor Ex", "Speed": "2"}

        # Mocking an object to be used for a property that has an embedded link
        embedded_get_mock.return_value.status_code = 200
        embedded_get_mock.return_value.json.return_value = state_object

        response, new_object_url = self.agent.put(collection_url, new_object)

        simplified_collection = \
            {
                "@context": "/serverapi/contexts/DroneCollection.jsonld",
                "@id": "/serverapi/DroneCollection/",
                "@type": "DroneCollection",
                "members": [
                    {
                        "@id": "/serverapi/DroneCollection/1",
                        "@type": "Drone"
                    },
                    {
                        "@id": "/serverapi/DroneCollection/2",
                        "@type": "Drone"
                    }
                ],
            }

        embedded_get_mock.return_value.json.return_value = \
            simplified_collection
        get_collection = self.agent.get(collection_url)
        self.assertEqual(type(get_collection), list)

    @patch('hydra_agent.agent.Session.get')
    @patch('hydra_agent.agent.Session.put')
    def test_put(self, put_session_mock, embedded_get_mock):
        """Tests put method from the Agent
        :param put_session_mock: MagicMock object for patching session.put
        """
        new_object = {"@type": "Drone", "DroneState": "/api/StateCollection/1",
                      "name": "Smart Drone", "model": "Hydra Drone",
                      "MaxSpeed": "999", "Sensor": "Wind"}

        collection_url = "http://localhost:8080/api/DroneCollection/"
        new_object_url = collection_url + "1"

        put_session_mock.return_value.status_code = 201
        put_session_mock.return_value.json.return_value = new_object
        put_session_mock.return_value.headers = {'Location': new_object_url}

        state_object = {"@context": "/api/contexts/StateCollection.jsonld",
                        "@id": "/api/StateCollection/1", "@type": "State",
                        "Battery": "sensor Ex", "Direction": "speed Ex",
                        "DroneID": "sensor Ex", "Position": "model Ex",
                        "SensorStatus": "sensor Ex", "Speed": "2"}

        # Mocking an object to be used for a property that has an embedded link
        embedded_get_mock.return_value.status_code = 200
        embedded_get_mock.return_value.json.return_value = state_object

        response, new_object_url = self.agent.put(collection_url, new_object)

        # Assert if object was inserted queried and inserted successfully
        get_new_object = self.agent.get(new_object_url)
        self.assertEqual(get_new_object, new_object)

    @patch('hydra_agent.agent.Session.get')
    @patch('hydra_agent.agent.Session.post')
    @patch('hydra_agent.agent.Session.put')
    def test_post(self, put_session_mock, post_session_mock,
                  embedded_get_mock):
        """Tests post method from the Agent
        :param put_session_mock: MagicMock object for patching session.put
        :param post_session_mock: MagicMock object for patching session.post
        """
        new_object = {"@type": "Drone", "DroneState": "/api/StateCollection/1",
                      "name": "Smart Drone", "model": "Hydra Drone",
                      "MaxSpeed": "999", "Sensor": "Wind"}

        collection_url = "http://localhost:8080/api/DroneCollection/"
        new_object_url = collection_url + "2"

        put_session_mock.return_value.status_code = 201
        put_session_mock.return_value.json.return_value = new_object
        put_session_mock.return_value.headers = {'Location': new_object_url}
        response, new_object_url = self.agent.put(collection_url, new_object)

        post_session_mock.return_value.status_code = 200
        post_session_mock.return_value.json.return_value = {"msg": "success"}
        new_object['name'] = "Updated Name"

        state_object = {"@context": "/api/contexts/StateCollection.jsonld",
                        "@id": "/api/StateCollection/1", "@type": "State",
                        "Battery": "sensor Ex", "Direction": "speed Ex",
                        "DroneID": "sensor Ex", "Position": "model Ex",
                        "SensorStatus": "sensor Ex", "Speed": "2"}
        # Mocking an object to be used for a property that has an embedded link
        embedded_get_mock.return_value.status_code = 200
        embedded_get_mock.return_value.json.return_value = state_object

        response = self.agent.post(new_object_url, new_object)

        # Assert if object was updated successfully as intended
        get_new_object = self.agent.get(new_object_url)
        self.assertEqual(get_new_object, new_object)

    @patch('hydra_agent.agent.Session.get')
    @patch('hydra_agent.agent.Session.delete')
    @patch('hydra_agent.agent.Session.put')
    def test_delete(self, put_session_mock, delete_session_mock,
                    get_session_mock):
        """Tests post method from the Agent
        :param put_session_mock: MagicMock object for patching session.put
        :param post_session_mock: MagicMock object for patching session.post
        """
        new_object = {"@type": "Drone", "DroneState": "/api/StateCollection/1",
                      "name": "Smart Drone", "model": "Hydra Drone",
                      "MaxSpeed": "999", "Sensor": "Wind"}

        collection_url = "http://localhost:8080/api/DroneCollection/"
        new_object_url = collection_url + "3"

        put_session_mock.return_value.status_code = 201
        put_session_mock.return_value.json.return_value = new_object
        put_session_mock.return_value.headers = {'Location': new_object_url}
        response, new_object_url = self.agent.put(collection_url, new_object)

        delete_session_mock.return_value.status_code = 200
        delete_session_mock.return_value.json.return_value = {"msg": "success"}
        response = self.agent.delete(new_object_url)

        get_session_mock.return_value.text = {"msg": "resource doesn't exist"}
        get_new_object = self.agent.get(new_object_url)

        # Assert if nothing different was returned by Redis
        self.assertEqual(get_new_object, {"msg": "resource doesn't exist"})

if __name__ == "__main__":
    unittest.main()
