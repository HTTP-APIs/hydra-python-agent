import pytest


@pytest.mark.usefixtures("handle_data")
class TestHandleData:
    """TestCase for HandleData Class"""

    @pytest.fixture(autouse=True)
    def load_data_mocks(self, mocker):
        self.mock_request = mocker.patch(
            "hydra_agent.querying_mechanism.urllib.request.urlopen", autospec=True
        )
        self.mock_json = mocker.patch(
            "hydra_agent.querying_mechanism.json.loads", autospec=True
        )

    def test_load_data(self, mocker):
        """Tests load_data method case without exceptions"""
        # mock to return byte code for response.read()
        intermediate_mock = mocker.MagicMock()
        intermediate_mock.__enter__.return_value.read.return_value = b"TestResponse"

        # making sure that request doesn't raise an exception
        self.mock_request.return_value = intermediate_mock

        # call load_data with url as param
        self.handle_data.load_data(self.test_url)

        # assert that json.loads was called with right params
        self.mock_json.assert_called_with("TestResponse")

    def test_load_data_with_errors(self, mocker):
        """Tests load_data method case with exception"""
        # logger_mock : MagicMock object from patching out the logger object
        mocker.patch("hydra_agent.querying_mechanism.logger")

        # request raises an exception (ValueError can be replaced by URLError or HTTPError)
        self.mock_request.side_effect = ValueError

        # Call load_data
        self.handle_data.load_data(self.test_url)

        # Assert that json.loads wasn't called
        self.mock_json.assert_not_called()


@pytest.mark.usefixtures("endpoint_query")
class TestEndpointQuery:
    """TestCase for EndpointQuery Class"""

    def test_get_allEndpoints(self, mocker):
        """Tests get_allEndpoints method"""
        # query to be passed as a param to get_allEndpoints
        query = "get endpoints"

        # connection_mock for connection attribute
        connection_mock = self.endpoint_query.connection

        # call to get_allEndpoints
        self.endpoint_query.get_allEndpoints(query)

        # asserting the connection.execute_command had calls with right parameters
        calls = [
            mocker.call("GRAPH.QUERY", "apigraph", "MATCH (p:classes) RETURN p"),
            mocker.call("GRAPH.QUERY", "apigraph", "MATCH (p:collection) RETURN p"),
        ]
        connection_mock.execute_command.assert_has_calls(calls)

    def test_get_classEndpoints(self, mocker):
        """Tests get_classEndpoints method"""
        # query to be passed as a param to get_classEndpoints
        query = "get classEndpoints"

        # connection_mock for connection attribute
        connection_mock = self.endpoint_query.connection

        # call to get_classEndpoints
        self.endpoint_query.get_classEndpoints(query)

        # asserting the connection.execute_command had calls with right parameters
        calls = [mocker.call("GRAPH.QUERY", "apigraph", "MATCH (p:classes) RETURN p")]
        connection_mock.execute_command.assert_has_calls(calls)

    def test_get_collectionEndpoints(self, mocker):
        """
        Tests get_collectionEndpoints method
        """
        # query to be passed as a param to get_collectionEndpoints
        query = "get collectionEndpoints"

        # connection_mock for connection attribute
        connection_mock = self.endpoint_query.connection

        # call to get_collectionEndpoints
        self.endpoint_query.get_collectionEndpoints(query)

        # asserting the connection.execute_command had calls with right parameters
        calls = [
            mocker.call("GRAPH.QUERY", "apigraph", "MATCH (p:collection) RETURN p")
        ]
        connection_mock.execute_command.assert_has_calls(calls)


@pytest.mark.usefixtures("collection_members_query")
class TestCollectionmembersQuery:
    """
    TestCase for CollectionmembersQuery class
    """

    def test_data_from_server(self, mocker):
        """
        Tests data_from_server method
        """
        # endpoint param to be passed to data_from_server
        endpoint = "TestEndpoint"

        load_server_mock = self.cmq.collection.load_from_server
        connection_mock = self.cmq.connection

        # call to data_from_server
        self.cmq.data_from_server(endpoint)

        # asserting that load_from_server was called with right params
        load_server_mock.assert_called_with(
            endpoint, self.cmq.api_doc, self.cmq.url, self.cmq.connection
        )

        # asserting that execute_command was called with right params
        calls = [
            mocker.call(
                "GRAPH.QUERY",
                "apigraph",
                'MATCH(p:collection) WHERE(p.type="TestEndpoint") RETURN p.members',
            )
        ]
        connection_mock.execute_command.assert_has_calls(calls)

    def smembers_mock_func(self, inp):
        """
        SideEffect for testing get_members

        Args:
            inp : Input to mock object's side effect equivalent to smembers method
        """
        if inp == "fs:endpoints":
            return [b"TestEndpoint"]

    def test_get_members_if(self):
        # query param to be passed to get_members
        """
        Tests get_members method when if condition passes
        """
        query = "TestEndpoint members"
        connection_mock = self.cmq.connection

        # making the if condition true
        connection_mock.keys.return_value = [b"fs:endpoints"]
        connection_mock.smembers.side_effect = self.smembers_mock_func

        # call to get_members
        self.cmq.get_members(query)

        # checking the call made to connection_mock.execute_command with correct params
        connection_mock.execute_command.assert_called_with(
            "GRAPH.QUERY",
            "apigraph",
            """MATCH(p:collection)
                   WHERE(p.type='TestEndpoint')
                   RETURN p.members""",
        )

        # asserting that connection.sadd was not called
        connection_mock.sadd.assert_not_called()

    def smembers_mock_func_else(self, inp):
        """
        SideEffect for mock object used in testing get_members_method

        Args:
            inp: Input to Mock object's side effect equivalent to smembers method
        """
        if inp == "fs:endpoints":
            return [b"TestEndpoint"]

    def test_get_members_else(self):
        """
        Tests get_members method when if condition fails
        """
        # query param to be passed to get_members
        query = "TestEndpoint members"
        connection_mock = self.cmq.connection

        # making the if condition false
        connection_mock.keys.return_value = []
        connection_mock.smembers.side_effect = self.smembers_mock_func_else

        # call to get_members
        self.cmq.get_members(query)

        # asserting that connection_mock.sadd was called
        connection_mock.sadd.assert_called_with("fs:endpoints", "TestEndpoint")


@pytest.mark.usefixtures("properties_query")
class TestPropertiesQuery:
    """
    TestCase for PropertiesQuery Class
    """

    def test_get_classes_properties(self):
        """
        Tests get_classes_properties method
        """
        # query param for get_classes_properties
        query = "classClassEndpoint properties"
        connection_mock = self.properties_query.connection

        # call to get_classes_properties
        self.properties_query.get_classes_properties(query)

        # asserting that redis_query was called with correct params
        connection_mock.execute_command.assert_called_with(
            "GRAPH.QUERY",
            "apigraph",
            'MATCH ( p:classes ) WHERE (p.type="ClassEndpoint") RETURN p.properties',
        )

    def test_get_collection_properties(self):
        """
        Tests get_collection_properties method
        """
        # query param for get_collection_properties
        query = "collectionEndpoint properties"
        connection_mock = self.properties_query.connection

        # call to get_collection_properties
        self.properties_query.get_collection_properties(query)

        # asserting that redis query was called with correct params
        connection_mock.execute_command.assert_called_with(
            "GRAPH.QUERY",
            "apigraph",
            'MATCH ( p:collection ) WHERE (p.type="collectionEndpoint") RETURN p.properties',
        )

    def test_members_properties(self):
        """
        Tests get_members_properties method
        """
        # query param for get_members_properties
        query = "testMember properties"

        connection_mock = self.properties_query.connection

        # call to get_members_properties
        self.properties_query.get_members_properties(query)

        # asserting that redis query was called with correct params
        connection_mock.execute_command.assert_called_with(
            "GRAPH.QUERY", "apigraph", "MATCH ( p:testMember ) RETURN p.id,p.properties"
        )

    def test_object_properties(self):
        """
        Tests get_object_property method
        """
        #  query for get_object_property
        query = "object/api/TestCollection/2 properties"

        connection_mock = self.properties_query.connection

        # call to get_object_property
        self.properties_query.get_object_property(query)

        # asserting that redis query was called with correct params
        connection_mock.execute_command.assert_called_with(
            "GRAPH.QUERY",
            "apigraph",
            'MATCH ( p:objectTest) WHERE (p.parent_id = "/api/TestCollection/2") RETURN p.properties',
        )


@pytest.mark.usefixtures("class_properties_value")
class TestClassPropertiesValue:
    """TestCase for ClassPropertiesValue"""

    @pytest.fixture(autouse=True)
    def load_data_mocks(self, mocker):
        self.mock_request = mocker.patch(
            "hydra_agent.querying_mechanism.urllib.request.urlopen", autospec=True
        )
        self.mock_json = mocker.patch(
            "hydra_agent.querying_mechanism.json.loads", autospec=True
        )

    def test_data_from_server(self, mocker):
        """
        Tests data_from_server method
        """
        # endpoint param for data_from_server
        endpoint = "TestEndpoint"
        clas_mock = self.cpv.clas
        connection_mock = self.cpv.connection
        mocker.patch.object(self.cpv.clas, "load_from_server")
        # call to data_from_server
        self.cpv.data_from_server(endpoint)
        # asserting that load_from_server was called with correct params
        clas_mock.load_from_server.assert_called_with(
            endpoint, self.cpv.api_doc, self.cpv.url, connection_mock
        )

        # asserting that redis_query was called with correct params
        connection_mock.execute_command.assert_called_with(
            "GRAPH.QUERY",
            "apigraph",
            """MATCH(p:classes)
               WHERE(p.type='TestEndpoint')
               RETURN p.property_value""",
        )

    def smembers_mock_func(self, inp):
        """
        SideEffect for mock object used in testing get_property_value
        Args:
            inp : Input to the SideEffect equivalent to smembers method
        """
        if inp == "fs:endpoints":
            return [b"TestClass"]

    def test_get_property_value(self):
        """
        Tests get_property_value when if condition passes
        """
        # query param for get_property_value
        query = "classTestClass property_value"
        connection_mock = self.cpv.connection

        # making the if condition true
        connection_mock.keys.return_value = [b"fs:endpoints"]
        connection_mock.smembers.side_effect = self.smembers_mock_func

        # call to get_members
        self.cpv.get_property_value(query)

        # checking the call made to connection_mock.execute_command with correct params
        connection_mock.execute_command.assert_called_with(
            "GRAPH.QUERY",
            "apigraph",
            """MATCH (p:classes)
                   WHERE (p.type = 'TestClass')
                   RETURN p.property_value""",
        )

        # asserting that connection.sadd was not called
        connection_mock.sadd.assert_not_called()

    def smembers_mock_func_else(self, inp):
        """
        SideEffect for mock object used in testing get_property_value
        """
        return []

    def test_get_property_value_else(self):
        """
        Tests get_property_value method when the if condition fails
        """
        # query param for get_property_value
        query = "classTestClass property_value"
        connection_mock = self.cpv.connection

        # making the if condition false
        connection_mock.keys.return_value = []
        connection_mock.smembers.side_effect = self.smembers_mock_func_else

        # call to get_members
        self.cpv.get_property_value(query)

        # asserting that connection.sadd was called
        connection_mock.sadd.assert_called_with("fs:endpoints", "TestClass")
