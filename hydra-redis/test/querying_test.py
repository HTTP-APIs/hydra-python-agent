import unittest
import urllib.request
import json
from hydrus.hydraspec import doc_maker
from os import sys, path
#import sys
#sys.path[0] = "/home/sandeep/gsoc_work/python-hydra-agent/hydra-redis"
#import querying_mechanism
#print(sys.path)
#import test
#import hydra_redis
PARENT_DIR = path.dirname(path.dirname(path.abspath(__file__)))
sys.path.append(PARENT_DIR)
import querying_mechanism


class TestQueryingMechanism(unittest.TestCase):

    def setUp(self):
        print("testing start:")

    def test_1_classendpoint(self):
        """Test for class endpoint"""
        check_data = [['p.id', 'p.operations', 'p.properties', 'p.type'],
                      ['vocab:EntryPoint/Location', 
                       "['POST'", "'PUT'", "'GET']", 
                       "['Location']", 'Location']]
        query = "show classEndpoints"
        data = query_facades.user_query(query)
        self.assertEqual(data,check_data)

    def test_2_collectionendpoint(self):
        """Test for collection endpoint"""
        check_data = ["ControllerLogCollection",
                      "DroneLogCollection",
                      "AnomalyCollection",
                      "DroneCollection",
                      "CommandCollection",
                      "HttpApiLogCollection",
                      "DatastreamCollection",
                      "MessageCollection"]
        query = "show collectionEndpoints"
        data = query_facades.user_query(query)
        for check in check_data:
            if check not in str(data):
                self.assertTrue(False)
        self.assertTrue(True)

    def test_3_CommandCollectionmember(self):
        """
        Test for all Commands in CommandCollection.
        Data is already stored in check_data from the static data url.
        Check_data is used for compare the data retrieve by querying process.
        """
        check_data = ['[]']
        query = "show CommandCollection members"
        data = query_facades.user_query(query)
        self.assertEqual(data[1],check_data)

    def test_4_ControllerLogCollectionmember(self):
        """
        Test for all controller logs for ControllerLogCollection.
        Whole object of ControllerLogCollection is stored in check data.
        Check_data is used for compare the data retrieve by querying process.
        """
        check_data = [{'@id': '/api/ControllerLogCollection/65',
                       '@type': 'ControllerLog'},
                      {'@id': '/api/ControllerLogCollection/183',
                       '@type': 'ControllerLog'},
                      {'@id': '/api/ControllerLogCollection/374',
                       '@type': 'ControllerLog'}]
        query = "show ControllerLogCollection members"
        data = query_facades.user_query(query)
        # Make data searchable and comaprable.
        data1 = str(data[1]).replace('"', '')
        # data retrive from the memory can be distributed:
        # like type can be at first position and id can be at second.
        # So, check_data split in 3 parts.
        # And check all parts are in data retrieve.
        if str(
            check_data[0]) in data1 and str(
            check_data[1]) in data1 and str(
                check_data[2]) in data1:
            self.assertTrue(True)
        else:
            self.assertTrue(False)
        

    def test_5_DatastreamCollectionmember(self):
        """Test for all datastream with Drone ID 2"""
        check_data = ['/api/DatastreamCollection/19']
        query = "show DatastreamCollection members"
        data = query_facades.user_query(query)
        # Here are find the datastream only for those which have DroneID 2.
        query = "show DroneID 2 and type Datastream"
        data = query_facades.user_query(query)
        self.assertEqual(data,check_data)


if __name__ == "__main__":
    url = "https://storage.googleapis.com/api3/api"
    vocab_url = url + "/" + "vocab"
    response = urllib.request.urlopen(vocab_url)
    apidoc = json.loads(response.read().decode('utf-8'))
    api_doc = doc_maker.create_doc(apidoc)
    query_facades = querying_mechanism.QueryFacades(api_doc, url, True)
    query_facades.initialize()
    unittest.main()
