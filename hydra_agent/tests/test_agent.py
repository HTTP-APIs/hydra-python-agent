import unittest
from unittest.mock import patch, MagicMock, call
from hydra_agent.agent import Agent
from hydra_agent.redis_core.graphutils_operations import GraphOperations
from hydra_agent.redis_core.redis_proxy import RedisProxy
from redisgraph import Graph
from hydra_agent.tests.test_examples.hydra_doc_sample import doc as drone_doc
from hydra_agent.helpers import expand_template
from urllib.parse import urlparse


class TestAgent(unittest.TestCase):
    """
    TestCase for Agent Class
    """

    @patch('hydra_agent.agent.socketio.Client.connect')
    @patch('hydra_agent.agent.Session.get')
    def setUp(self, get_session_mock, socket_client_mock):
        """Setting up Agent object
        :param get_session_mock: MagicMock object for patching session.get
                                 it's used to Mock Hydrus response to ApiDoc
        """
        # Mocking get for ApiDoc to Server, so hydrus doesn't need to be up
        get_session_mock.return_value.json.return_value = drone_doc
        socket_client_mock.return_value = None

        self.agent = Agent("http://localhost:8080/api")
        self.redis_proxy = RedisProxy()
        self.redis_connection = self.redis_proxy.get_connection()
        self.redis_graph = Graph("apigraph", self.redis_connection)

    @patch('hydra_agent.agent.Session.get')
    def test_get_url(self, get_session_mock):
        """Tests get method from the Agent with URL
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
        """Tests get method from the Agent by class name and properties
        :param get_session_mock: MagicMock object for patching session.get
        """
        state_object = {"@id": "/api/StateCollection/1", "@type": "State",
                        "Battery": "sensor Ex", "Direction": "North",
                        "DroneID": "sensor Ex", "Position": "model Ex",
                        "SensorStatus": "sensor Ex", "Speed": "2",
                        "@context": "/api/contexts/StateCollection.jsonld"}

        get_session_mock.return_value.status_code = 200
        get_session_mock.return_value.json.return_value = state_object
        response_url = self.agent.get("http://localhost:8080/api/" +
                                      "StateCollection/1")

        response_cached = self.agent.get(resource_type="State",
                                         filters={"Direction": "North"},
                                         cached_limit=1)

        response_cached = response_cached[0]
        self.assertEqual(response_url, response_cached)

        response_not_cached = self.agent.get("http://localhost:8080/api/" +
                                             "StateCollection/1")
        self.assertEqual(response_not_cached, response_cached)

    @patch('hydra_agent.agent.Session.get')
    @patch('hydra_agent.agent.Session.put')
    def test_get_collection(self, put_session_mock, embedded_get_mock):
        """Tests get method from the Agent when fetching collections
        :param put_session_mock: MagicMock object for patching session.put
        :param embedded_get_mock: MagicMock object for patching session.get
        """
        new_object = {"@type": "Drone", "DroneState": "1",
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
                "@context": "/api/contexts/DroneCollection.jsonld",
                "@id": "/api/DroneCollection/",
                "@type": "DroneCollection",
                "members": [
                    {
                        "@id": "/api/DroneCollection/1",
                        "@type": "Drone"
                    }
                ],
                "search": {
                    "@type": "hydra:IriTemplate",
                    "hydra:mapping": [{
                        "@type": "hydra:IriTemplateMapping",
                        "hydra:property": "http://auto.schema.org/speed",
                        "hydra:required": False,
                        "hydra:variable": "DroneState[Speed]"}
                    ],
                    "hydra:template": "/serverapi/Drone(DroneState[Speed])",
                    "hydra:variableRepresentation": "hydra:BasicRepresentation",
                },
                "totalItems": 1,
                "view": {
                    "@id": "/serverapi/DroneCollection?page=1",
                    "@type": "PartialCollectionView",
                    "first": "/serverapi/DroneCollection?page=1",
                    "last": "/serverapi/DroneCollection?page=1",
                    "next": "/serverapi/DroneCollection?page=1"
                }
            }

        embedded_get_mock.return_value.json.return_value = simplified_collection
        get_collection_url = self.agent.get(collection_url)
        get_collection_resource_type = self.agent.get(resource_type="Drone")
        self.assertEqual(type(get_collection_url), dict)
        self.assertEqual(type(get_collection_resource_type), dict)
        self.assertEqual(get_collection_resource_type, get_collection_url)
        get_collection_cached = self.agent.get(resource_type="Drone",
                                               cached_limit=1)
        self.assertEqual(get_collection_cached[0]["@id"],
                         get_collection_url['members'][0]["@id"])

    @patch('hydra_agent.agent.Session.get')
    @patch('hydra_agent.agent.Session.put')
    def test_put(self, put_session_mock, embedded_get_mock):
        """Tests put method from the Agent
        :param put_session_mock: MagicMock object for patching session.put
        :param embedded_get_mock: MagicMock object for patching session.get
        """
        new_object = {"@type": "Drone", "DroneState": "1",
                      "name": "Smart Drone", "model": "Hydra Drone",
                      "MaxSpeed": "999", "Sensor": "Wind"}

        class_url = "http://localhost:8080/api/Drone/"
        new_object_url = class_url + "1"

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

        response, new_object_url = self.agent.put(new_object_url, new_object)

        # Assert if object was inserted queried and inserted successfully
        get_new_object_url = self.agent.get(new_object_url)
        self.assertEqual(get_new_object_url, new_object)

        get_new_object_type = self.agent.get(resource_type="Drone",
                                             filters={'name': "Smart Drone"},
                                             cached_limit=1)
        self.assertEqual(get_new_object_url, get_new_object_type[0])

    @patch('hydra_agent.agent.Session.get')
    @patch('hydra_agent.agent.Session.post')
    @patch('hydra_agent.agent.Session.put')
    def test_post(self, put_session_mock, post_session_mock,
                  embedded_get_mock):
        """Tests post method from the Agent
        :param put_session_mock: MagicMock object for patching session.put
        :param post_session_mock: MagicMock object for patching session.post
        """
        new_object = {"@type": "Drone", "DroneState": "1",
                      "name": "Smart Drone", "model": "Hydra Drone",
                      "MaxSpeed": "999", "Sensor": "Wind"}

        class_url = "http://localhost:8080/api/Drone/"
        new_object_url = class_url + "2"

        put_session_mock.return_value.status_code = 201
        put_session_mock.return_value.json.return_value = new_object
        put_session_mock.return_value.headers = {'Location': new_object_url}
        response, new_object_url = self.agent.put(new_object_url, new_object)

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
        :param delete_session_mock: MagicMock object to patch session.delete
        :param get_session_mock: MagicMock object for patching session.get
        """
        new_object = {"@type": "Drone", "DroneState": "/api/StateCollection/1",
                      "name": "Smart Drone", "model": "Hydra Drone",
                      "MaxSpeed": "999", "Sensor": "Wind"}

        class_url = "http://localhost:8080/api/Drone/"
        new_object_url = class_url + "3"

        put_session_mock.return_value.status_code = 201
        put_session_mock.return_value.json.return_value = new_object
        put_session_mock.return_value.headers = {'Location': new_object_url}
        response, new_object_url = self.agent.put(new_object_url, new_object)

        delete_session_mock.return_value.status_code = 200
        delete_session_mock.return_value.json.return_value = {"msg": "success"}
        response = self.agent.delete(new_object_url)

        get_session_mock.return_value.text = {"msg": "resource doesn't exist"}
        get_new_object = self.agent.get(new_object_url)

        # Assert if nothing different was returned by Redis
        self.assertEqual(get_new_object, {"msg": "resource doesn't exist"})

    def test_basic_iri_templates(self):
        """Tests the URI constructed on the basis of Basic Representation
        """
        simplified_response = {
            "@context": "/serverapi/contexts/DroneCollection.jsonld",
            "@id": "/serverapi/DroneCollection/",
            "@type": "DroneCollection",
            "members": [
                {
                    "@id": "/serverapi/DroneCollection/1",
                    "@type": "Drone"
                },
            ],
            "search": {
                "@type": "hydra:IriTemplate",
                "hydra:mapping": [
                    {
                        "@type": "hydra:IriTemplateMapping",
                        "hydra:property": "http://schema.org/name",
                        "hydra:required": False,
                        "hydra:variable": "name"
                    },
                    {
                        "@type": "hydra:IriTemplateMapping",
                        "hydra:property": "pageIndex",
                        "hydra:required": False,
                        "hydra:variable": "pageIndex"
                    },
                    {
                        "@type": "hydra:IriTemplateMapping",
                        "hydra:property": "limit",
                        "hydra:required": False,
                        "hydra:variable": "limit"
                    },
                    {
                        "@type": "hydra:IriTemplateMapping",
                        "hydra:property": "offset",
                        "hydra:required": False,
                        "hydra:variable": "offset"
                    }
                ],
                "hydra:template": "/serverapi/(pageIndex, limit, offset)",
                "hydra:variableRepresentation": "hydra:BasicRepresentation"
            },

            "view": {
                "@id": "/serverapi/DroneCollection?page=1",
                "@type": "PartialCollectionView",
                "first": "/serverapi/DroneCollection?page=1",
                "last": "/serverapi/DroneCollection?page=1",
                "next": "/serverapi/DroneCollection?page=1"
            }
        }
        sample_mapping_object = {
            "name": "Drone1",
            "pageIndex": "1",
            "limit": "10",
            "offset": "1"
        }
        url = urlparse(expand_template(
            "http://localhost:8080/serverapi/DroneCollection", simplified_response, sample_mapping_object))
        url_should_be = urlparse(
            "http://localhost:8080/serverapi/DroneCollection?name=Drone1&pageIndex=1&limit=10&offset=1")

        self.assertEqual(sorted(url.query), sorted(url_should_be.query))

    def test_explicit_iri_templates(self):
        """Tests the URI constructed on the basis of Basic Representation
        """
        simplified_response = {
            "@context": "/serverapi/contexts/DroneCollection.jsonld",
            "@id": "/serverapi/DroneCollection/",
            "@type": "DroneCollection",
            "members": [
                {
                    "@id": "/serverapi/DroneCollection/1",
                    "@type": "Drone"
                },
            ],
            "search": {
                "@type": "hydra:IriTemplate",
                "hydra:mapping": [
                    {
                        "@type": "hydra:IriTemplateMapping",
                        "hydra:property": "http://schema.org/name",
                        "hydra:required": False,
                        "hydra:variable": "name"
                    },
                    {
                        "@type": "hydra:IriTemplateMapping",
                        "hydra:property": "pageIndex",
                        "hydra:required": False,
                        "hydra:variable": "pageIndex"
                    },
                    {
                        "@type": "hydra:IriTemplateMapping",
                        "hydra:property": "limit",
                        "hydra:required": False,
                        "hydra:variable": "limit"
                    },
                    {
                        "@type": "hydra:IriTemplateMapping",
                        "hydra:property": "offset",
                        "hydra:required": False,
                        "hydra:variable": "offset"
                    }
                ],
                "hydra:template": "/serverapi/(pageIndex, limit, offset)",
                "hydra:variableRepresentation": "hydra:ExplicitRepresentation"
            },
            "view": {
                "@id": "/serverapi/DroneCollection?page=1",
                "@type": "PartialCollectionView",
                "first": "/serverapi/DroneCollection?page=1",
                "last": "/serverapi/DroneCollection?page=1",
                "next": "/serverapi/DroneCollection?page=1"
            }
        }
        sample_mapping_object = {
            "url_demo": {
                "@id": "http://www.hydra-cg.com/"
            },
            "prop_with_language": {
                "@language": "en",
                "@value": "A simple string"
            },
            "prop_with_type": {
                "@value": "5.5",
                "@type": "http://www.w3.org/2001/XMLSchema#decimal"
            },
            "str_prop": "A simple string"
        }
        url = urlparse(expand_template(
            "http://localhost:8080/serverapi/DroneCollection", simplified_response, sample_mapping_object))
        url_should_be = urlparse(
            "http://localhost:8080/serverapi/DroneCollection?url_demo=http%3A%2F%2Fwww.hydra-cg.com%2F&prop_with_language=%22A%20simple%20string%22%40en&prop_with_type=%225.5%22%5E%5Ehttp%3A%2F%2Fwww.w3.org%2F2001%2FXMLSchema%23decimal&str_prop=%22A%20simple%20string%22")

        self.assertEqual(sorted(url.query), sorted(url_should_be.query))

    @patch('hydra_agent.agent.Session.get')
    @patch('hydra_agent.agent.Session.put')
    def test_edges(self, put_session_mock, embedded_get_mock):
        """Tests to check if all edges are being created properly
        :param put_session_mock: MagicMock object for patching session.put
        :param embedded_get_mock: MagicMock object for patching session.get
        """
        new_object = {"@type": "Drone", "DroneState": {
                      "@type": "State", "Battery": "C1WE92", "Direction": "Q9VV88", "DroneID": "6EBGT5", "Position": "A"
                      , "SensorStatus": "335Y8B", "Speed": "IZPSTE"},
                      "name": "Smart Drone", "model": "Hydra Drone",
                      "MaxSpeed": "999", "Sensor": "Wind"}

        class_url = "http://localhost:8080/api/Drone/"
        new_object_url = class_url + "1"

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

        response, new_object_url = self.agent.put(class_url, new_object)

        # Checking if Drone Collection has an edge to the Drone Resource
        query = "MATCH (p)-[r]->() WHERE p.type = 'Drone' \
            RETURN type(r)"
        query_result = self.redis_graph.query(query)
        breakpoint()
        self.assertEqual(query_result.result_set[0][0], 'has_Drone')

        # Checking if State Collection has an edge to the State Resource
        query = "MATCH (p)-[r]->() WHERE p.type = 'State' \
            RETURN type(r)"
        query_result = self.redis_graph.query(query)
        self.assertEqual(query_result.result_set[0][0], 'has_State')

        # Checking if Drone Resource has an edge to the State Resource
        query = "MATCH (p)-[r]->() WHERE p.type = 'Drone' RETURN type(r)"
        query_result = self.redis_graph.query(query)
        self.assertEqual(query_result.result_set[0][0], 'has_State')


if __name__ == "__main__":
    unittest.main()
