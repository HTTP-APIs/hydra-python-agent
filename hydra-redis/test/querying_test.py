import unittest
import urllib.request
import json
from hydrus.hydraspec import doc_maker
from os import sys, path

PARENT_DIR = path.dirname(path.dirname(path.abspath(__file__)))
sys.path.append(PARENT_DIR)
import querying_mechanism


class Tests:

    def endpointTest(self):
        """Test for all the endpoints class + collection endpoints"""
        query = "show endpoints"
        data = query_facades.user_query(query)
        if len(data) == 11:
            return True
        else:
            return False

    def classendpointTest(self):
        """Test for class endpoint"""
        query = "show classEndpoints"
        data = query_facades.user_query(query)
        if len(data) == 2:
            return True
        else:
            return False

    def collectionendpointTest(self):
        """Test for collection endpoint"""
        query = "show collectionEndpoints"
        data = query_facades.user_query(query)
        if len(data) == 9:
            return True
        else:
            return False

    def CommandCollectionmemberTest(self):
        """
        Test for all Commands in CommandCollection.
        Data is already stored in check_data from the static data url.
        Check_data is used for compare the data retrieve by querying process.
        """
        check_data = ['[]']
        query = "show CommandCollection members"
        data = query_facades.user_query(query)
        if data[1] == check_data:
            return True
        else:
            return False

    def ControllerLogCollectionmemberTest(self):
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
            return True
        else:
            return False

    def DatastreamCollectionmemberTest(self):
        """Test for all datastream with Drone ID 2"""
        check_data = ['/api/DatastreamCollection/19']
        query = "show DatastreamCollection members"
        data = query_facades.user_query(query)
        # Here are find the datastream only for those which have DroneID 2.
        query = "show DroneID 2 and type Datastream"
        data = query_facades.user_query(query)
        if data == check_data:
            return True
        else:
            return False


class TestQueryingMechanism(unittest.TestCase):
    query_test = Tests()

    def test_1_endpoint(self):
        self.assertTrue(self.query_test.endpointTest())

    def test_2_classendpoint(self):
        self.assertTrue(self.query_test.classendpointTest())

    def test_3_collectionendpoint(self):
        self.assertTrue(self.query_test.collectionendpointTest())

    def test_4_CommandCollectionmember(self):
        self.assertTrue(self.query_test.CommandCollectionmemberTest())

    def test_5_ControllerLogCollectionmember(self):
        self.assertTrue(self.query_test.ControllerLogCollectionmemberTest())

    def test_6_DatastreamCollectionmember(self):
        self.assertTrue(self.query_test.DatastreamCollectionmemberTest())


if __name__ == "__main__":
    url = "https://storage.googleapis.com/api3/api"
    vocab_url = url + "/" + "vocab"
    response = urllib.request.urlopen(vocab_url)
    apidoc = json.loads(response.read().decode('utf-8'))
    api_doc = doc_maker.create_doc(apidoc)
    query_facades = querying_mechanism.QueryFacades(api_doc, url, True)
    query_facades.initialize()
    unittest.main()
