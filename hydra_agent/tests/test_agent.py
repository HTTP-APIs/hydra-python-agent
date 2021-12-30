import pytest
from hydra_agent.agent import Agent
from hydra_agent.helpers import expand_template
from urllib.parse import urlparse


@pytest.mark.usefixtures("setup_agent_for_tests")
class TestAgent:
    """TestCase for Agent Class"""

    @pytest.fixture(autouse=True)
    def init_agent(self, constants):
        """Setting up Agent object"""
        try:
            self.agent = Agent(constants["entrypoint_url"])
        except (SyntaxError, ConnectionResetError):
            self.init_agent(constants["entrypoint_url"])

    def test_get_url(self, get_session_mock, state_object):
        """Tests get method from the Agent with URL"""
        get_session_mock.return_value.status_code = 200
        get_session_mock.return_value.json.return_value = state_object
        response = self.agent.get(self.entrypoint_url + "State/1")

        assert response == state_object

    def test_get_class_properties(self, get_session_mock, state_object):
        """Tests get method from the Agent by class name and properties"""

        get_session_mock.return_value.status_code = 200
        get_session_mock.return_value.json.return_value = state_object
        response_url = self.agent.get("http://localhost:8080/api/" + "State/1")

        response_cached = self.agent.get(
            resource_type="State", filters={"Direction": "North"}, cached_limit=1
        )

        response_cached = response_cached[0]
        assert response_url == response_cached

        response_not_cached = self.agent.get("http://localhost:8080/api/" + "State/1")
        assert response_not_cached == response_cached

    def test_get_collection(
        self, get_session_mock, put_session_mock, simplified_collection
    ):
        """Tests get method from the Agent when fetching collections"""

        new_object = {"@type": "DroneCollection", "members": ["1"]}

        collection_url = "http://localhost:8080/api/DroneCollection/"
        new_collection_url = collection_url + "1"

        put_session_mock.return_value.status_code = 201
        put_session_mock.return_value.json.return_value = new_object
        put_session_mock.return_value.headers = {"Location": new_collection_url}

        get_session_mock.return_value.json.return_value = simplified_collection
        get_session_mock.return_value.status_code = 200
        response, new_object_url = self.agent.put(collection_url, new_object)
        get_collection_url = self.agent.get(collection_url)
        assert type(get_collection_url) == dict
        # get_collection_cached = self.agent.get(resource_type="Drone",
        #                                        cached_limit=1)
        # self.assertEqual(get_collection_cached[0]["@id"],
        #                  get_collection_url['members'][0]["@id"])

    def test_put(
        self,
        mocker,
        get_session_mock,
        put_session_mock,
        new_object,
        state_object,
        drone_res,
    ):
        """Tests put method from the Agent"""

        class_url = "http://localhost:8080/api/Drone/"
        new_object_url = class_url + "1"

        put_session_mock.return_value.status_code = 201
        put_session_mock.return_value.json.return_value = new_object
        put_session_mock.return_value.headers = {"Location": new_object_url}

        fake_responses = [mocker.Mock(), mocker.Mock(), mocker.Mock(), mocker.Mock()]
        fake_responses[0].json.return_value = drone_res
        fake_responses[0].status_code = 200
        fake_responses[1].json.return_value = state_object
        fake_responses[1].status_code = 200
        fake_responses[2].json.return_value = drone_res
        fake_responses[2].status_code = 200
        fake_responses[3].json.return_value = drone_res
        fake_responses[3].status_code = 200
        # Mocking an object to be used for a property that has an embedded link
        get_session_mock.return_value.status_code = 200
        get_session_mock.side_effect = fake_responses
        response, new_object_url = self.agent.put(new_object_url, new_object)

        # Assert if object was inserted queried and inserted successfully
        get_new_object_url = self.agent.get(new_object_url)
        assert get_new_object_url == drone_res

        get_new_object_type = self.agent.get(
            new_object_url, filters={"name": "Smart Drone"}
        )
        assert get_new_object_url == get_new_object_type

    def test_post(
        self,
        put_session_mock,
        post_session_mock,
        get_session_mock,
        new_object,
        state_object,
        drone_res,
        mocker,
    ):
        """Tests post method from the Agent"""
        class_url = "http://localhost:8080/api/Drone/"
        new_object_url = class_url + "2"

        put_session_mock.return_value.status_code = 201
        put_session_mock.return_value.json.return_value = new_object
        put_session_mock.return_value.headers = {"Location": new_object_url}

        fake_responses = [mocker.Mock(), mocker.Mock(), mocker.Mock()]
        fake_responses[0].json.return_value = drone_res
        fake_responses[0].status_code = 200
        fake_responses[1].json.return_value = state_object
        fake_responses[1].status_code = 200
        # Mocking an object to be used for a property that has an embedded link
        get_session_mock.return_value.status_code = 200
        get_session_mock.side_effect = fake_responses

        response, new_object_url = self.agent.put(new_object_url, new_object)

        post_session_mock.return_value.status_code = 200
        post_session_mock.return_value.json.return_value = {"msg": "success"}
        new_object["DroneState"]["@id"] = "/api/State/1"
        new_object["name"] = "Updated Name"
        # Mocking an object to be used for a property that has an embedded link
        response = self.agent.post(new_object_url, new_object)
        # Assert if object was updated successfully as intended
        fake_responses[2].json.return_value = new_object
        fake_responses[2].status_code = 200
        get_new_object = self.agent.get(new_object_url)

        assert get_new_object == new_object

    def test_delete(
        self,
        put_session_mock,
        delete_session_mock,
        get_session_mock,
        mocker,
        new_object,
        state_object,
        drone_res,
    ):
        """Tests post method from the Agent"""

        class_url = "http://localhost:8080/api/Drone/"
        new_object_url = class_url + "3"

        put_session_mock.return_value.status_code = 201
        put_session_mock.return_value.json.return_value = new_object
        put_session_mock.return_value.headers = {"Location": new_object_url}
        fake_responses = [mocker.Mock(), mocker.Mock(), mocker.Mock()]
        fake_responses[0].json.return_value = drone_res
        fake_responses[0].status_code = 200
        fake_responses[1].json.return_value = state_object
        fake_responses[1].status_code = 200
        fake_responses[2].text = {"msg": "resource doesn't exist"}
        # Mocking an object to be used for a property that has an embedded link
        get_session_mock.return_value.status_code = 200
        get_session_mock.side_effect = fake_responses

        response, new_object_url = self.agent.put(new_object_url, new_object)

        delete_session_mock.return_value.status_code = 200
        delete_session_mock.return_value.json.return_value = {"msg": "success"}
        response = self.agent.delete(new_object_url)
        get_new_object = self.agent.get(new_object_url)

        # Assert if nothing different was returned by Redis
        assert get_new_object == {"msg": "resource doesn't exist"}

    def test_basic_iri_templates(self):
        """Tests the URI constructed on the basis of Basic Representation"""
        simplified_response = {
            "@context": "/serverapi/contexts/DroneCollection.jsonld",
            "@id": "/serverapi/DroneCollection/",
            "@type": "DroneCollection",
            "members": [
                {"@id": "/serverapi/DroneCollection/1", "@type": "Drone"},
            ],
            "search": {
                "@type": "hydra:IriTemplate",
                "hydra:mapping": [
                    {
                        "@type": "hydra:IriTemplateMapping",
                        "hydra:property": "http://schema.org/name",
                        "hydra:required": False,
                        "hydra:variable": "name",
                    },
                    {
                        "@type": "hydra:IriTemplateMapping",
                        "hydra:property": "pageIndex",
                        "hydra:required": False,
                        "hydra:variable": "pageIndex",
                    },
                    {
                        "@type": "hydra:IriTemplateMapping",
                        "hydra:property": "limit",
                        "hydra:required": False,
                        "hydra:variable": "limit",
                    },
                    {
                        "@type": "hydra:IriTemplateMapping",
                        "hydra:property": "offset",
                        "hydra:required": False,
                        "hydra:variable": "offset",
                    },
                ],
                "hydra:template": "/serverapi/(pageIndex, limit, offset)",
                "hydra:variableRepresentation": "hydra:BasicRepresentation",
            },
            "view": {
                "@id": "/serverapi/DroneCollection?page=1",
                "@type": "PartialCollectionView",
                "first": "/serverapi/DroneCollection?page=1",
                "last": "/serverapi/DroneCollection?page=1",
                "next": "/serverapi/DroneCollection?page=1",
            },
        }
        sample_mapping_object = {
            "name": "Drone1",
            "pageIndex": "1",
            "limit": "10",
            "offset": "1",
        }
        url = urlparse(
            expand_template(
                "http://localhost:8080/serverapi/DroneCollection",
                simplified_response,
                sample_mapping_object,
            )
        )
        url_should_be = urlparse(
            "http://localhost:8080/serverapi/DroneCollection?name=Drone1&pageIndex=1&limit=10&offset=1"
        )

        assert sorted(url.query) == sorted(url_should_be.query)

    def test_explicit_iri_templates(self):
        """Tests the URI constructed on the basis of Basic Representation"""
        simplified_response = {
            "@context": "/serverapi/contexts/DroneCollection.jsonld",
            "@id": "/serverapi/DroneCollection/",
            "@type": "DroneCollection",
            "members": [
                {"@id": "/serverapi/DroneCollection/1", "@type": "Drone"},
            ],
            "search": {
                "@type": "hydra:IriTemplate",
                "hydra:mapping": [
                    {
                        "@type": "hydra:IriTemplateMapping",
                        "hydra:property": "http://schema.org/name",
                        "hydra:required": False,
                        "hydra:variable": "name",
                    },
                    {
                        "@type": "hydra:IriTemplateMapping",
                        "hydra:property": "pageIndex",
                        "hydra:required": False,
                        "hydra:variable": "pageIndex",
                    },
                    {
                        "@type": "hydra:IriTemplateMapping",
                        "hydra:property": "limit",
                        "hydra:required": False,
                        "hydra:variable": "limit",
                    },
                    {
                        "@type": "hydra:IriTemplateMapping",
                        "hydra:property": "offset",
                        "hydra:required": False,
                        "hydra:variable": "offset",
                    },
                ],
                "hydra:template": "/serverapi/(pageIndex, limit, offset)",
                "hydra:variableRepresentation": "hydra:ExplicitRepresentation",
            },
            "view": {
                "@id": "/serverapi/DroneCollection?page=1",
                "@type": "PartialCollectionView",
                "first": "/serverapi/DroneCollection?page=1",
                "last": "/serverapi/DroneCollection?page=1",
                "next": "/serverapi/DroneCollection?page=1",
            },
        }
        sample_mapping_object = {
            "url_demo": {"@id": "http://www.hydra-cg.com/"},
            "prop_with_language": {"@language": "en", "@value": "A simple string"},
            "prop_with_type": {
                "@value": "5.5",
                "@type": "http://www.w3.org/2001/XMLSchema#decimal",
            },
            "str_prop": "A simple string",
        }
        url = urlparse(
            expand_template(
                "http://localhost:8080/serverapi/DroneCollection",
                simplified_response,
                sample_mapping_object,
            )
        )
        url_should_be = urlparse(
            "http://localhost:8080/serverapi/DroneCollection?url_demo=http%3A%2F%2Fwww.hydra-cg.com%2F&prop_with_language=%22A%20simple%20string%22%40en&prop_with_type=%225.5%22%5E%5Ehttp%3A%2F%2Fwww.w3.org%2F2001%2FXMLSchema%23decimal&str_prop=%22A%20simple%20string%22"
        )

        assert sorted(url.query) == sorted(url_should_be.query)

    def test_edges(
        self,
        put_session_mock,
        get_session_mock,
        new_object,
        state_object,
        drone_res,
        mocker,
    ):
        """Tests to check if all edges are being created properly"""

        class_url = "http://localhost:8080/api/Drone/"
        new_object_url = class_url + "1"

        put_session_mock.return_value.status_code = 201
        put_session_mock.return_value.json.return_value = new_object
        put_session_mock.return_value.headers = {"Location": new_object_url}

        fake_responses = [mocker.Mock(), mocker.Mock()]
        fake_responses[0].json.return_value = drone_res
        fake_responses[0].status_code = 200
        fake_responses[1].json.return_value = state_object
        fake_responses[1].status_code = 200
        # Mocking an object to be used for a property that has an embedded link
        get_session_mock.return_value.status_code = 200
        get_session_mock.side_effect = fake_responses
        response, new_object_url = self.agent.put(class_url, new_object)
        # Checking if Drone Class has an edge to the Drone Resource
        query = "MATCH (p)-[r]->() WHERE p.type = 'Drone' \
            RETURN type(r)"
        query_result = self.redis_graph.query(query)
        assert query_result.result_set[0][0] == "has_Drone"

        # Checking if State  has an edge to the State Resource
        query = "MATCH (p)-[r]->() WHERE p.type = 'State' \
            RETURN type(r)"
        query_result = self.redis_graph.query(query)
        assert query_result.result_set[0][0] == "has_State"

        # Checking if Drone Resource has an edge to the State Resource
        query = "MATCH (p)-[r]->() WHERE p.type = 'Drone' RETURN type(r)"
        query_result = self.redis_graph.query(query)
        assert query_result.result_set[1][0] == "has_State"
