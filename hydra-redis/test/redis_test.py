import unittest
import redis


class Tests:
    def entry_point(self):
        """Test for testing the data stored in entrypoint endpoint"""

        print("entrypoint")
        r = redis.StrictRedis()
        reply = r.execute_command('GRAPH.QUERY',
                                  'apidoc', "MATCH (p:id) RETURN p")
        property_list = []
        flag = 0
        for objects in reply:
            for obj in objects:
                if flag == 0:
                    string = obj.decode('utf-8')
                    map_string = map(str.strip, string.split(','))
                    property_list = list(map_string)
                    check = property_list.pop()
                    property_list.append(check.replace("\x00", ""))
                    print(property_list)
                    flag += 1
                    break
        if ("p.id" in property_list and
                "p.url" in property_list and
                "p.supportedOperation" in property_list):
            return True
        else:
            return False

    def collection_endpoints(self):
        """Test for testing the data stored in collection endpoints"""

        print("collection endpoints")
        r = redis.StrictRedis()
        reply = r.execute_command('GRAPH.QUERY',
                                  'apidoc', "MATCH (p:collection) RETURN p")
        property_list = []
        flag = 0
        for objects in reply:
            for obj in objects:
                if flag == 0:
                    string = obj.decode('utf-8')
                    map_string = map(str.strip, string.split(','))
                    property_list = list(map_string)
                    check = property_list.pop()
                    property_list.append(check.replace("\x00", ""))
                    print(property_list)
                    flag += 1
                    break
        if ("p.id" in property_list and
                "p.operations" in property_list and
                "p.members" in property_list):
            return True
        else:
            return False

    def class_endpoints(self):
        """Test for testing the data stored in classes endpoints"""

        print("class endpoints")
        r = redis.StrictRedis()
        reply = r.execute_command('GRAPH.QUERY',
                                  'apidoc', "MATCH (p:classes) RETURN p")
        property_list = []
        flag = 0
        for objects in reply:
            for obj in objects:
                if flag == 0:
                    string = obj.decode('utf-8')
                    map_string = map(str.strip, string.split(','))
                    property_list = list(map_string)
                    check = property_list.pop()
                    property_list.append(check.replace("\x00", ""))
                    print(property_list)
                    flag += 1
                    break
        if ("p.id" in property_list and
                "p.operations" in property_list and
                "p.properties" in property_list and
                "p.type" in property_list):
            return True
        else:
            return False


class TestRedisStructure(unittest.TestCase):
    test_redis = Tests()

    def test_entrypoint(self):
        self.assertTrue(self.test_redis.entry_point())

    def test_collectionEndpoints(self):
        self.assertTrue(self.test_redis.collection_endpoints())

    def test_classEndpoints(self):
        self.assertTrue(self.test_redis.class_endpoints())


if __name__ == '__main__':
    unittest.main()
