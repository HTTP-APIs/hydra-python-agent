import redis
import pytest
from pytest_mock import mocker


@pytest.mark.usefixtures("init_db_for_redis_tests")
class TestRedisStructure:
    def test_entrypoint(self, redis_reply, redis_db_execute_command_query):
        """Test for testing the data stored in entrypoint endpoint.
        `redis_reply` is data which will get from redis_db_0 on `query` execution.
        """
        query = ("GRAPH.QUERY", "apigraph", "MATCH (p:id) RETURN p")
        property_list = redis_reply[0][0]

        assert (
            b"p.id" in property_list
            and b"p.url" in property_list
            and b"p.supportedOperation" in property_list
        ) == True

    def test_collectionEndpoints(self, redis_reply, redis_db_execute_command_query):
        """
        Test for testing the data stored in collection endpoints
        `redis_reply` is data which will get from redis_db_0 on `query` execution.
        """
        query = ("GRAPH.QUERY", "apigraph", "MATCH (p:collection) RETURN p")
        property_list = redis_reply[0][0]

        assert (
            b"p.id" in property_list
            and b"p.operations" in property_list
            and b"p.type" in property_list
        ) == True

    def test_classEndpoints(self, redis_reply, redis_db_execute_command_query):
        """
        Test for testing the data stored in classes endpoints
        `redis_reply` is data which will get from redis_db_0 on `query` execution.
        """
        query = ("GRAPH.QUERY", "apigraph", "MATCH (p:classes) RETURN p")
        property_list = redis_reply[0][0]
        assert (
            b"p.id" in property_list
            and b"p.operations" in property_list
            and b"p.properties" in property_list
            and b"p.type" in property_list
        ) == True
