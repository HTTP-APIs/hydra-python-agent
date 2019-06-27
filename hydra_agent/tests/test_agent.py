import unittest
from unittest.mock import patch, MagicMock, call
from hydra_agent.agent import Agent
from hydra_agent.graphutils_operations import GraphOperations
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

        get_session_mock.return_value.json.return_value = drone_doc

        self.agent = Agent("http://localhost:8080/serverapi")

    @patch('hydra_agent.agent.Session.get')
    @patch('hydra_agent.agent.GraphOperations.get_processing')
    def test_get(self, get_processing_mock, get_session_mock):
        """Tests get method from the Agent
        :param get_mock: MagicMock object for patching session.get
        """
        mock_dict = {"@type": "Drone", "DroneState": "Simplified state",
                     "name": "Smart Drone", "model": "Hydra Drone",
                     "MaxSpeed": "999", "Sensor": "Wind"}
        get_session_mock.return_value.status_code = 200
        get_session_mock.return_value.json.return_value = mock_dict
        response = self.agent.get("http://localhost:8080/serverapi/" +
                                  "DroneCollection/1")

        get_processing_mock.assert_called_with("http://localhost:8080/server" +
                                               "api/DroneCollection/1",
                                               mock_dict)
        self.assertEqual(response, mock_dict)

    # THIS IS STILL FAILLING BECAUSE OF SOME HYDRUS MOCKING THAT I'M WORKING ON
    @patch('hydra_agent.agent.Session.put')
    @patch('hydra_agent.agent.GraphOperations.put_processing')
    def test_put(self, put_processing_mock, put_session_mock):
        """Tests get method from the Agent
        :param get_mock: MagicMock object for patching session.get
        """
        new_object = {"@type": "Drone", "DroneState": "Simplified state",
                      "name": "Smart Drone", "model": "Hydra Drone",
                      "MaxSpeed": "999", "Sensor": "Wind"}

        collection_url = "http://localhost:8080/serverapi/DroneCollection/"
        new_object_url = collection_url + "1"

        mock = MagicMock()
        mock.headers['Location'] = new_object_url

        put_session_mock.return_value.status_code = 201
        put_session_mock.return_value.json.return_value = new_object
        put_session_mock.return_value['headers']['Location'] = new_object_url
        response, new_object_url = self.agent.put(collection_url, new_object)

        put_processing_mock.assert_called_with(new_object_url, new_object)

        get_new_object = self.agent.get(new_object_url)
        self.assertEqual(get_new_object, new_object)

if __name__ == "__main__":
    unittest.main()
