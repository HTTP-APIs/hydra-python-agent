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


@pytest.fixture(scope="class")
def handle_data(request):
    """Setting up HandleData object"""
    request.cls.test_url = "TestURL"
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
def test_database():
    """Initialize redis database"""
    test_db = redis.StrictRedis(host="localhost", port=6379, db=5)
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
