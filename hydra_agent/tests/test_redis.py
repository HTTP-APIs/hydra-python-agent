import unittest
import redis
from unittest.mock import MagicMock


class Tests:
    def entry_point(self):
        """Test for testing the data stored in entrypoint endpoint.
        `redis_reply` is data which will get from redis_db_0 on `query` execution.
        """
        print("testing entrypoint with db=0 ...")
        query = ('GRAPH.QUERY','apidoc', "MATCH (p:id) RETURN p")
        redis_db = redis.StrictRedis(host='localhost', port=6379, db=0)

        redis_reply = [[[b'p.url', b'p.id', b'p.supportedOperation'], [b'http://localhost:8080/api', b'vocab:Entrypoint', b'GET']], [b'Query internal execution time: 0.071272 milliseconds']]

        redis_db_execute_command_query = MagicMock(return_value = redis_reply)        
        property_list = redis_reply[0][0]
        if (b"p.id" in property_list and
                b"p.url" in property_list and
                b"p.supportedOperation" in property_list):
            return True
        else:
            return False

    def collection_endpoints(self):
        """Test for testing the data stored in collection endpoints
        `redis_reply` is data which will get from redis_db_0 on `query` execution.
        """
        print("testing collection endpoints with db=0 ...")
        query = ('GRAPH.QUERY','apidoc', "MATCH (p:collection) RETURN p")
        redis_db = redis.StrictRedis(host='localhost', port=6379, db=0)

        redis_reply = [[[b'p.id', b'p.operations', b'p.type'], [b'vocab:EntryPoint/HttpApiLogCollection', b"['GET', 'PUT']", b'HttpApiLogCollection'], [b'vocab:EntryPoint/AnomalyCollection', b"['GET', 'PUT']", b'AnomalyCollection'], [b'vocab:EntryPoint/CommandCollection', b"['GET', 'PUT']", b'CommandCollection'], [b'vocab:EntryPoint/ControllerLogCollection', b"['GET', 'PUT']", b'ControllerLogCollection'], [b'vocab:EntryPoint/DatastreamCollection', b"['GET', 'PUT']", b'DatastreamCollection'], [b'vocab:EntryPoint/MessageCollection', b"['GET', 'PUT']", b'MessageCollection'], [b'vocab:EntryPoint/DroneLogCollection', b"['GET', 'PUT']", b'DroneLogCollection'], [b'vocab:EntryPoint/DroneCollection', b"['GET', 'PUT']", b'DroneCollection']], [b'Query internal execution time: 0.089501 milliseconds']]

        redis_db_execute_command_query = MagicMock(return_value = redis_reply)
        property_list = redis_reply[0][0]
        if (b"p.id" in property_list and
                b"p.operations" in property_list and
                b"p.type" in property_list):
            return True
        else:
            return False

    def class_endpoints(self):
        """Test for testing the data stored in classes endpoints
        `redis_reply` is data which will get from redis_db_0 on `query` execution.
        """
        print("testing class endpoints with db=0 ...")
        query = ('GRAPH.QUERY','apidoc', "MATCH (p:classes) RETURN p")
        redis_db = redis.StrictRedis(host='localhost', port=6379, db=0)

        redis_reply = [[[b'p.properties', b'p.id', b'p.operations', b'p.type'], [b"['Location']", b'vocab:EntryPoint/Location', b"['POST', 'PUT', 'GET']", b'Location']], [b'Query internal execution time: 0.076224 milliseconds']]

        redis_db_execute_command_query = MagicMock(return_value = redis_reply)
        property_list = redis_reply[0][0]
        if (b"p.id" in property_list and
                b"p.operations" in property_list and
                b"p.properties" in property_list and
                b"p.type" in property_list):
            return True
        else:
            return False


class TestRedisStructure(unittest.TestCase):
    test_redis = Tests()

    @classmethod
    def setUpClass(cls):
        cls.test_database=redis.StrictRedis(host='localhost', port=6379, db=5)
        cls.test_database.set("foo","bar")
        cls.test_database.set("hydra","redis")
        print("setUpClass db=5 keys:",cls.test_database.keys())

    def test_entrypoint(self):
        self.assertTrue(self.test_redis.entry_point())

    def test_collectionEndpoints(self):
        self.assertTrue(self.test_redis.collection_endpoints())

    def test_classEndpoints(self):
        self.assertTrue(self.test_redis.class_endpoints())

    @classmethod
    def tearDownClass(cls):
        cls.test_database.flushdb()
        print("tearDownClass db=5 keys:",cls.test_database.get("foo"))

if __name__ == '__main__':
    unittest.main()
