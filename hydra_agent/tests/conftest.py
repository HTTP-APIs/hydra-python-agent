import pytest
from hydra_agent.querying_mechanism import HandleData
from hydra_agent.querying_mechanism import (
    EndpointQuery,
    CollectionmembersQuery,
    PropertiesQuery,
    ClassPropertiesValue,
)
import redis
import os
from hydra_agent.redis_core.redis_proxy import RedisProxy
from redisgraph import Graph
from hydra_agent.tests.test_examples.hydra_doc_sample import doc as drone_doc


@pytest.fixture(scope="class")
def handle_data(request, constants):
    """Setting up HandleData object"""
    request.cls.test_url = constants["test_url"]
    request.cls.handle_data = HandleData()


@pytest.fixture(scope="class")
def endpoint_query(request, class_mocker):
    """Setting up EndpointQuery object"""
    class_mocker.patch("hydra_agent.querying_mechanism.RedisProxy", autospec=True)
    request.cls.endpoint_query = EndpointQuery()


@pytest.fixture(scope="class")
def collection_members_query(request, class_mocker):
    """Setting up CollectionmembersQuery object"""
    class_mocker.patch(
        "hydra_agent.querying_mechanism.CollectionEndpoints", autospec=True
    )
    class_mocker.patch("hydra_agent.querying_mechanism.RedisProxy", autospec=True)
    api_doc, url, graph = (class_mocker.MagicMock() for i in range(3))
    request.cls.cmq = CollectionmembersQuery(api_doc, url, graph)


@pytest.fixture(scope="class")
def properties_query(request, class_mocker):
    """Setting up PropertiesQuery object"""
    class_mocker.patch("hydra_agent.querying_mechanism.RedisProxy", autospec=True)
    request.cls.properties_query = PropertiesQuery()


@pytest.fixture(scope="class")
def class_properties_value(request, class_mocker):
    """Setting up ClassPropertiesValue object"""
    class_mocker.patch(
        "hydra_agent.querying_mechanism.CollectionEndpoints", autospec=True
    )
    class_mocker.patch("hydra_agent.querying_mechanism.RedisProxy", autospec=True)
    api_doc, url, graph = (class_mocker.MagicMock() for i in range(3))
    request.cls.cpv = ClassPropertiesValue(api_doc, url, graph)


@pytest.fixture(scope="module")
def test_database(constants):
    """Initialize redis database"""
    test_db = redis.StrictRedis(
        host=constants["host"], port=constants["redis_port"], db=5
    )
    yield test_db
    test_db.flushdb()


@pytest.fixture(scope="module")
def init_db_for_redis_tests(test_database):
    """Initialize the database by adding key, value pairs"""
    test_database.set("foo", "bar")
    test_database.set("hydra", "redis")


@pytest.fixture
def redis_reply():
    """Returns the correct response on processing query"""
    test_method_name = (
        os.environ.get("PYTEST_CURRENT_TEST").split(":")[-1].split(" ")[0].lower()
    )
    if "collection" in test_method_name:
        return [
            [
                [b"p.id", b"p.operations", b"p.type"],
                [
                    b"vocab:EntryPoint/HttpApiLogCollection",
                    b"['GET', 'PUT']",
                    b"HttpApiLogCollection",
                ],
                [
                    b"vocab:EntryPoint/AnomalyCollection",
                    b"['GET', 'PUT']",
                    b"AnomalyCollection",
                ],
                [
                    b"vocab:EntryPoint/CommandCollection",
                    b"['GET', 'PUT']",
                    b"CommandCollection",
                ],
                [
                    b"vocab:EntryPoint/ControllerLogCollection",
                    b"['GET', 'PUT']",
                    b"ControllerLogCollection",
                ],
                [
                    b"vocab:EntryPoint/DatastreamCollection",
                    b"['GET', 'PUT']",
                    b"DatastreamCollection",
                ],
                [
                    b"vocab:EntryPoint/MessageCollection",
                    b"['GET', 'PUT']",
                    b"MessageCollection",
                ],
                [
                    b"vocab:EntryPoint/DroneLogCollection",
                    b"['GET', 'PUT']",
                    b"DroneLogCollection",
                ],
                [
                    b"vocab:EntryPoint/DroneCollection",
                    b"['GET', 'PUT']",
                    b"DroneCollection",
                ],
            ],
            [b"Query internal execution time: 0.089501 milliseconds"],
        ]
    elif "class" in test_method_name:
        return [
            [
                [b"p.properties", b"p.id", b"p.operations", b"p.type"],
                [
                    b"['Location']",
                    b"vocab:EntryPoint/Location",
                    b"['POST', 'PUT', 'GET']",
                    b"Location",
                ],
            ],
            [b"Query internal execution time: 0.076224 milliseconds"],
        ]
    elif "entrypoint" in test_method_name:
        return [
            [
                [b"p.url", b"p.id", b"p.supportedOperation"],
                [b"http://localhost:8080/api", b"vocab:Entrypoint", b"GET"],
            ],
            [b"Query internal execution time: 0.071272 milliseconds"],
        ]


@pytest.fixture
def redis_db_execute_command_query(redis_reply, mocker):
    return mocker.MagicMock(return_value=redis_reply)


@pytest.fixture(scope="module")
def constants():
    """Constants for tests"""
    return {
        "host": "localhost",
        "test_url": "TestURL",
        "redis_port": 6379,
        "entrypoint_url": "http://localhost:8080/serverapi/",
        "api_name": "serverapi",
        "graph_name": "apigraph",
    }


@pytest.fixture(scope="class")
def setup_agent_for_tests(class_mocker, request, constants):
    """Setting up RedisProxy and Graph for Agent"""
    socket_client_mock = class_mocker.patch("hydra_agent.agent.socketio.Client.connect")
    get_session_mock = class_mocker.patch("hydra_agent.agent.Session.get")
    # Mocking get for ApiDoc to Server, so hydrus doesn't need to be up
    get_session_mock.return_value.json.return_value = drone_doc
    socket_client_mock.return_value = None
    request.cls.redis_proxy = RedisProxy()
    request.cls.redis_connection = request.cls.redis_proxy.get_connection()
    request.cls.redis_graph = Graph(
        constants["graph_name"], request.cls.redis_connection
    )
    request.cls.entrypoint_url = constants["entrypoint_url"]


@pytest.fixture
def get_session_mock(mocker):
    """Mock for patching GET request"""
    return mocker.patch("hydra_agent.agent.Session.get")


@pytest.fixture
def put_session_mock(mocker):
    """Mock for patching PUT request"""
    return mocker.patch("hydra_agent.agent.Session.put")


@pytest.fixture
def post_session_mock(mocker):
    """Mock for patching POST request"""
    return mocker.patch("hydra_agent.agent.Session.post")


@pytest.fixture
def delete_session_mock(mocker):
    """Mock for patching DELETE request"""
    return mocker.patch("hydra_agent.agent.Session.delete")


@pytest.fixture
def state_object(constants):
    """Dummy drone state object for tests"""
    state_object = {
        "@context": "/api/contexts/State.jsonld",
        "@id": "/api/State/1",
        "@type": "State",
        "Battery": "sensor Ex",
        "Direction": "North",
        "DroneID": "sensor Ex",
        "Position": "model Ex",
        "SensorStatus": "sensor Ex",
        "Speed": "2",
    }
    return state_object


@pytest.fixture
def simplified_collection(constants):
    """Dummy collection for tests"""
    return {
        "@context": f"/{constants['api_name']}/contexts/DroneCollection.jsonld",
        "@id": f"/{constants['api_name']}/DroneCollection/1",
        "@type": "DroneCollection",
        "members": [{"@id": f"/{constants['api_name']}/Drone/1", "@type": "Drone"}],
        "search": {
            "@type": "hydra:IriTemplate",
            "hydra:mapping": [
                {
                    "@type": "hydra:IriTemplateMapping",
                    "hydra:property": "http://auto.schema.org/speed",
                    "hydra:required": False,
                    "hydra:variable": "DroneState[Speed]",
                }
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
            "next": "/serverapi/DroneCollection?page=1",
        },
    }


@pytest.fixture
def new_object():
    """Dummy drone object for tests"""
    new_object = {
        "@type": "Drone",
        "DroneState": {
            "@type": "State",
            "Battery": "C1WE92",
            "Direction": "Q9VV88",
            "DroneID": "6EBGT5",
            "Position": "A",
            "SensorStatus": "335Y8B",
            "Speed": "IZPSTE",
        },
        "MaxSpeed": "A3GZ37",
        "Sensor": "E7JD5Q",
        "model": "HB14CX",
        "name": "Smart Drone",
    }
    return new_object


@pytest.fixture
def drone_res(constants):
    """Dummy drone response for tests"""
    drone_res = {
        "@context": "/api/contexts/Drone.jsonld",
        "@id": "/api/Drone/1",
        "@type": "Drone",
        "DroneState": {
            "@id": "/api/State/1",
            "@type": "State",
            "Battery": "C1WE92",
            "Direction": "Q9VV88",
            "DroneID": "6EBGT5",
            "Position": "A",
            "SensorStatus": "335Y8B",
            "Speed": "IZPSTE",
        },
        "MaxSpeed": "A3GZ37",
        "Sensor": "E7JD5Q",
        "model": "HB14CX",
        "name": "Smart Drone",
    }
    return drone_res
