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


class TestEndpointQuery(unittest.TestCase):
    @patch('hydra_agent.querying_mechanism.RedisProxy', autospec=True)
    def setUp(self, redis_mock):
        self.endpoint_query = EndpointQuery()

    def test_get_allEndpoints(self):
        # query to be passed as a param to get_allEndpoints
        query = "get endpoints"

        # connection_mock for connection attribute
        connection_mock = self.endpoint_query.connection

        # call to get_allEndpoints
        self.endpoint_query.get_allEndpoints(query)

        # asserting the connection.execute_command had calls with right parameters
        calls = [call('GRAPH.QUERY', 'apidoc', 'MATCH (p:classes) RETURN p'), call('GRAPH.QUERY', 'apidoc',
                 'MATCH (p:collection) RETURN p')]
        connection_mock.execute_command.assert_has_calls(calls)

    def test_get_classEndpoints(self):
        # query to be passed as a param to get_classEndpoints
        query = "get classEndpoints"

        # connection_mock for connection attribute
        connection_mock = self.endpoint_query.connection

        # call to get_classEndpoints
        self.endpoint_query.get_classEndpoints(query)

        # asserting the connection.execute_command had calls with right parameters
        calls = [call('GRAPH.QUERY', 'apidoc', 'MATCH (p:classes) RETURN p')]
        connection_mock.execute_command.assert_has_calls(calls)

    def test_get_collectionEndpoints(self):
        # query to be passed as a param to get_collectionEndpoints
        query = "get collectionEndpoints"

        # connection_mock for connection attribute
        connection_mock = self.endpoint_query.connection

        # call to get_collectionEndpoints
        self.endpoint_query.get_collectionEndpoints(query)

        # asserting the connection.execute_command had calls with right parameters
        calls = [call('GRAPH.QUERY', 'apidoc',
            'MATCH (p:collection) RETURN p')]
        connection_mock.execute_command.assert_has_calls(calls)


class TestCollectionmembersQuery(unittest.TestCase):
    @patch('hydra_agent.querying_mechanism.CollectionEndpoints', autospec=True)
    @patch('hydra_agent.querying_mechanism.RedisProxy', autospec=True)
    def setUp(self, redis_mock, collections_mock):
        api_doc = MagicMock()
        url = MagicMock()
        graph = MagicMock()
        self.cmq = CollectionmembersQuery(api_doc, url, graph)

    def test_data_from_server(self):
        # endpoint param to be passed to data_from_server
        endpoint = "TestEndpoint"

        load_server_mock = self.cmq.collection.load_from_server
        connection_mock = self.cmq.connection

        # call to data_from_server
        self.cmq.data_from_server(endpoint)

        # asserting that load_from_server was called with right params
        load_server_mock.assert_called_with(endpoint,
                self.cmq.api_doc,
                self.cmq.url,
                self.cmq.connection)

        # asserting that execute_command was called with right params
        calls = [call('GRAPH.QUERY', 'apidoc', 'MATCH(p:collection) WHERE(p.type="TestEndpoint") RETURN p.members')]
        connection_mock.execute_command.assert_has_calls(calls)

    def smembers_mock_func(self, inp):
        if inp == "fs:endpoints":
            return [b"TestEndpoint"]

    def test_get_members_if(self):
        query = "TestEndpoint members"
        connection_mock = self.cmq.connection

        connection_mock.keys.return_value = [b'fs:endpoints']
        connection_mock.smembers.side_effect = self.smembers_mock_func
        self.cmq.get_members(query)

        connection_mock.execute_command.assert_called_with('GRAPH.QUERY', 'apidoc', """MATCH(p:collection)
                   WHERE(p.type='TestEndpoint')
                   RETURN p.members""")

        connection_mock.sadd.assert_not_called()

    def smembers_mock_func_else(self, inp):
        if inp == "fs:endpoints":
            return [b"TestEndpoint"]

    def test_get_members_else(self):
        query = "TestEndpoint members"
        connection_mock = self.cmq.connection

        connection_mock.keys.return_value = []
        connection_mock.smembers.side_effect = self.smembers_mock_func_else

        self.cmq.get_members(query)

        connection_mock.sadd.assert_called_with("fs:endpoints", "TestEndpoint")


class TestPropertiesQuery(unittest.TestCase):
    @patch('hydra_agent.querying_mechanism.RedisProxy')
    def setUp(self, redis_mock):
        self.properties_query = PropertiesQuery()

    def test_get_classes_properties(self):
        query = "classClassEndpoint properties"
        connection_mock = self.properties_query.connection

        self.properties_query.get_classes_properties(query)

        connection_mock.execute_command.assert_called_with('GRAPH.QUERY', 'apidoc', 'MATCH ( p:classes ) WHERE (p.type="ClassEndpoint") RETURN p.properties')

    def test_get_collection_properties(self):
        query = "collectionEndpoint properties"

        connection_mock = self.properties_query.connection

        self.properties_query.get_collection_properties(query)

        connection_mock.execute_command.assert_called_with('GRAPH.QUERY', 'apidoc', 'MATCH ( p:collection ) WHERE (p.type="collectionEndpoint") RETURN p.properties')

    def test_members_properties(self):
        query = "testMember properties"

        connection_mock = self.properties_query.connection

        self.properties_query.get_members_properties(query)

        connection_mock.execute_command.assert_called_with('GRAPH.QUERY', 'apidoc', 'MATCH ( p:testMember ) RETURN p.id,p.properties')

    def test_object_properties(self):
        query = "object/api/TestCollection/2 properties"

        connection_mock = self.properties_query.connection

        self.properties_query.get_object_property(query)

        connection_mock.execute_command.assert_called_with('GRAPH.QUERY', 'apidoc', 'MATCH ( p:objectTest) WHERE (p.parent_id = "/api/TestCollection/2") RETURN p.properties')


class TestClassPropertiesValue(unittest.TestCase):
    @patch('hydra_agent.querying_mechanism.ClassEndpoints', autospec=True)
    @patch('hydra_agent.querying_mechanism.RedisProxy')
    def setUp(self, redis_mock, classEndpoint_mock):
        api_doc = MagicMock()
        url = MagicMock()
        graph = MagicMock()
        self.cpv = ClassPropertiesValue(api_doc, url, graph)

    def test_data_from_server(self):
        endpoint = "TestEndpoint"
        clas_mock = self.cpv.clas
        connection_mock = self.cpv.connection

        self.cpv.data_from_server(endpoint)

        clas_mock.load_from_server.assert_called_with(endpoint, self.cpv.api_doc, self.cpv.url, connection_mock)

        connection_mock.execute_command.assert_called_with('GRAPH.QUERY', 'apidoc', """MATCH(p:classes)
               WHERE(p.type='TestEndpoint')
               RETURN p.property_value""")


if __name__ == "__main__":
    unittest.main()
