import unittest
from unittest.mock import MagicMock


class TestQueryingMechanism(unittest.TestCase):

    def test_1_classendpoint(self):
        """Test for class endpoint"""
        check_data = [['p.properties', 'p.id', 'p.type'],
                      ["['Location']",'vocab:EntryPoint/Location','Location']]
        query = "show classEndpoints"
        EndpointQuery_get_classEndpoints = MagicMock(return_value=check_data)
        data = EndpointQuery_get_classEndpoints(query)
        print("testing classEndpoints...")
        assert data == check_data


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
        EndpointQuery_get_collectionEndpoints = MagicMock(
                                                    return_value=check_data)
        data = EndpointQuery_get_collectionEndpoints(query)
        print("testing collectionEndpoints...")
        assert data == check_data


    def test_3_CommandCollectionmember(self):
        """
        Test for all Commands in CommandCollection.
        """
        check_data = ['[]']
        query = "show CommandCollection members"
        CollectionmembersQuery_get_members =MagicMock(return_value=check_data)
        data = CollectionmembersQuery_get_members(query)
        print("testing CommandCollection members...")
        assert data==check_data


    def test_4_ControllerLogCollectionmember(self):
        """
        Test for all controller logs for ControllerLogCollection.
        Whole object of ControllerLogCollection is stored in check data.
        """
        check_data = [{'@id': '/api/ControllerLogCollection/65',
                       '@type': 'ControllerLog'},
                      {'@id': '/api/ControllerLogCollection/183',
                       '@type': 'ControllerLog'},
                      {'@id': '/api/ControllerLogCollection/374',
                       '@type': 'ControllerLog'}]
        query = "show ControllerLogCollection members"
        CollectionmembersQuery_get_members =MagicMock(return_value=check_data)
        data = CollectionmembersQuery_get_members(query)
        print("testing ControllerLogCollection members...")
        assert data == check_data


    def test_5_DatastreamCollectionmember(self):
        """Test for all datastream with Drone ID 2"""
        check_data = ['/api/DatastreamCollection/19']
        query = "show DatastreamCollection members"
        CollectionmembersQuery_get_members =MagicMock(return_value=check_data)
        data = CollectionmembersQuery_get_members(query)
        # Here are find the datastream only for those which have DroneID 2.
        query = "show DroneID 2 and type Datastream"
        CompareProperties_object_property_comparison_list = MagicMock(return_value=check_data)
        data = CompareProperties_object_property_comparison_list(query)
        print("testing DatastreamCollection members...")
        assert data == check_data


if __name__ == "__main__":
    unittest.main()
