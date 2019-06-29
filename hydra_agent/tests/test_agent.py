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

        self.agent = Agent("http://localhost:8080/serverapi")

    @patch('hydra_agent.agent.Session.get')
    @patch('hydra_agent.agent.GraphOperations.get_processing')
    def test_get(self, get_processing_mock, get_session_mock):
        """Tests get method from the Agent
        :param get_processing_mock: MagicMock object to patch graphoperations
        :param get_mock: MagicMock object for patching session.get
        """
        mock_dict = {"@type": "Drone", "DroneState": "Simplified state",
                     "name": "Smart Drone", "model": "Hydra Drone",
                     "MaxSpeed": "999", "Sensor": "Wind"}

        # Mock server request to the Server
        get_session_mock.return_value.status_code = 200
        get_session_mock.return_value.json.return_value = mock_dict
        response = self.agent.get("http://localhost:8080/serverapi/" +
                                  "DroneCollection/1")

        get_processing_mock.assert_called_with("http://localhost:8080/server" +
                                               "api/DroneCollection/1",
                                               mock_dict)
        self.assertEqual(response, mock_dict)

    @patch('hydra_agent.agent.Session.put')
    def test_put(self, put_session_mock):
        """Tests put method from the Agent
        :param put_session_mock: MagicMock object for patching session.put
        """
        new_object = {"@type": "Drone", "DroneState": "Simplified state",
                      "name": "Smart Drone", "model": "Hydra Drone",
                      "MaxSpeed": "999", "Sensor": "Wind"}

        collection_url = "http://localhost:8080/serverapi/DroneCollection/"
        new_object_url = collection_url + "1"

        put_session_mock.return_value.status_code = 201
        put_session_mock.return_value.json.return_value = new_object
        put_session_mock.return_value.headers = {'Location': new_object_url}
        response, new_object_url = self.agent.put(collection_url, new_object)

        # Assert if object was inserted queried and inserted successfully
        get_new_object = self.agent.get(new_object_url)
        self.assertEqual(get_new_object, new_object)

    @patch('hydra_agent.agent.Session.post')
    @patch('hydra_agent.agent.Session.put')
    def test_post(self, put_session_mock, post_session_mock):
        """Tests post method from the Agent
        :param put_session_mock: MagicMock object for patching session.put
        :param post_session_mock: MagicMock object for patching session.post
        """
        new_object = {"@type": "Drone", "DroneState": "Simplified state",
                      "name": "Smart Drone", "model": "Hydra Drone",
                      "MaxSpeed": "999", "Sensor": "Wind"}

        collection_url = "http://localhost:8080/serverapi/DroneCollection/"
        new_object_url = collection_url + "2"

        put_session_mock.return_value.status_code = 201
        put_session_mock.return_value.json.return_value = new_object
        put_session_mock.return_value.headers = {'Location': new_object_url}
        response, new_object_url = self.agent.put(collection_url, new_object)

        post_session_mock.return_value.status_code = 200
        post_session_mock.return_value.json.return_value = {"msg": "success"}
        new_object['name'] = "Updated Name"
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
        new_object = {"@type": "Drone", "DroneState": "Simplified state",
                      "name": "Smart Drone", "model": "Hydra Drone",
                      "MaxSpeed": "999", "Sensor": "Wind"}

        collection_url = "http://localhost:8080/serverapi/DroneCollection/"
        new_object_url = collection_url + "3"

        put_session_mock.return_value.status_code = 201
        put_session_mock.return_value.json.return_value = new_object
        put_session_mock.return_value.headers = {'Location': new_object_url}
        response, new_object_url = self.agent.put(collection_url, new_object)

        delete_session_mock.return_value.status_code = 200
        delete_session_mock.return_value.json.return_value = {"msg": "success"}
        response = self.agent.delete(new_object_url)

        get_session_mock.return_value.json.return_value = {"msg": "success"}
        get_new_object = self.agent.get(new_object_url)

        # Assert if nothing different was returned by Redis
        self.assertEqual(get_new_object, {"msg": "success"})

if __name__ == "__main__":
    unittest.main()
