import unittest
from unittest.mock import patch, MagicMock, call
from hydra_agent.querying_mechanism import HandleData, logger
from hydra_agent.querying_mechanism import EndpointQuery, CollectionmembersQuery, PropertiesQuery, ClassPropertiesValue


class TestHandleData(unittest.TestCase):
    def setUp(self):
        self.handle_data = HandleData()

    @patch('hydra_agent.querying_mechanism.json.loads', spec_set=True)
    @patch('hydra_agent.querying_mechanism.urllib.request.urlopen', spec_set=True)
    def test_load_data(self, request_mock, json_mock):
        # url passed to load_data as an argument
        url = "TestURL"

        # mock to return byte code for response.read()
        intermediate_mock = MagicMock()
        intermediate_mock.read.return_value = b"TestResponse"

        # making sure that request doesn't raise an exception
        request_mock.return_value = intermediate_mock

        # call load_data with url as param
        self.handle_data.load_data(url)

        # assert that json.loads was called with right params
        json_mock.assert_called_with("TestResponse")

    @patch('hydra_agent.querying_mechanism.json.loads', spec_set=True)
    @patch('hydra_agent.querying_mechanism.logger')
    @patch('hydra_agent.querying_mechanism.urllib.request.urlopen', spec_set=True)
    def test_load_data_with_errors(self, request_mock, logger_mock, json_mock):
        # url passed to load_data as an argument
        url = "TestURL"
        # request raises an exception (ValueError can be replaced by URLError or HTTPError)
        request_mock.side_effect = ValueError

        # Call load_data
        self.handle_data.load_data(url)

        # Assert that json.loads wasn't called
        json_mock.assert_not_called()
