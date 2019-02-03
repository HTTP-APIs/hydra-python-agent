import random
import string
import logging
from redisgraph import Graph
from core.utils.help import help
from core.utils.encode_result import encode_result
from core.utils.redis_proxy import RedisProxy
from core.utils.handle_data import HandleData
from hydra_graph import InitialGraph
from hydra_python_core.doc_maker import create_doc
from core.utils.collections_endpoint import CollectionEndpoints
from core.utils.classes_objects import ClassEndpoints, RequestError
from core.end_point_query import EndPointQuery
from core.utils.check_url import check_url_exist

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CollectionMembersQuery:
    """
    CollectionMembersQuery is used for fetching members of any
    CollectionEndpoints.
    It fetches data from the server and adds it to the redis graph.

    Attributes:
        connection(RedisProxy): An instance of redis client.


    """

    def __init__(self, api_doc, url, graph):
        self.connection = RedisProxy.get_connection()
        self.api_doc = api_doc
        self.url = url
        self._data = HandleData.load_data(self.url)
        self.graph = graph
        self.collection = CollectionEndpoints(
            graph.redis_graph, graph.class_endpoints, api_doc)

    def data_from_server(self, endpoint):
        """
        Load data from the server for first time.

        Args:
            endpoint: collectionEndpoint to load members from.

        :return: get data from the Redis memory.
        """
        self.collection.load_from_server(
            endpoint, self.api_doc, self.url, self.connection
        )

        graphQuery = 'MATCH (p:collection) WHERE(p.type="{}") RETURN p.members'.format(
            endpoint
        )
        resultData = self.graph.redis_graph.query(graphQuery)
        encode_result(resultData)

        print("Collection {} Members -- \n".format(endpoint))
        resultData.pretty_print()

        return resultData.result_set

    def get_members(self, query):
        """
        Gets Data from the Redis.
        :param query: query get from the user, Ex: DroneCollection members
        :return: get data from the Redis memory.
        """
        endpoint = query.replace(" members", "")
        if str.encode("fs:endpoints") in self.connection.keys() and str.encode(
            endpoint
        ) in self.connection.smembers("fs:endpoints"):
            get_data = self.connection.execute_command(
                "GRAPH.QUERY",
                "apidoc",
                """MATCH(p:collection)
                   WHERE(p.type='{}')
                   RETURN p.members""".format(
                    endpoint
                ),
            )
            print(endpoint, " members")
            return self._data.show_data(get_data)

        else:
            self.connection.sadd("fs:endpoints", endpoint)
            print(self.connection.smembers("fs:endpoints"))
            return self.data_from_server(endpoint)


class PropertiesQuery:
    """
    PropertiesQuery is used for all properties for alltypes of  nodes like:
    classes or collection endpoints, members,object.
    """

    def __init__(self):
        self.redis_connection = RedisProxy()
        self.handle_data = HandleData()
        self.connection = self.redis_connection.get_connection()
        self._data = self.handle_data

    def get_classes_properties(self, query):
        """
        Show the given type of property of given Class endpoint.
        :param query: get query from the user, Ex: classLocation properties
        :return: get data from the Redis memory.
        """
        query = query.replace("class", "")
        endpoint, query = query.split(" ")
        get_data = self.connection.execute_command(
            "GRAPH.QUERY",
            "apidoc",
            'MATCH ( p:classes ) WHERE (p.type="{}") RETURN p.{}'.format(
                endpoint, query
            ),
        )
        print("class", endpoint, query)
        return self._data.show_data(get_data)

    def get_collection_properties(self, query):
        """
        Show the given type of property of given collection endpoint.
        :param query: get query from the user, Ex: DroneCollection properties.
        :return: get data from the Redis memory.
        """
        endpoint, query = query.split(" ")

        get_data = self.connection.execute_command(
            "GRAPH.QUERY",
            "apidoc",
            'MATCH ( p:collection ) WHERE (p.type="{}") RETURN p.{}'.format(
                endpoint, query
            ),
        )

        print("collection", endpoint, query)
        return self._data.show_data(get_data)

    def get_members_properties(self, query):
        """
        Show the given type of property of given member.
        :param query: gete query from the user, Ex: objectsDrone properties
        :return: get data from the Redis memory.
        """
        endpoint, query = query.split(" ")
        get_data = self.connection.execute_command(
            "GRAPH.QUERY",
            "apidoc",
            "MATCH ( p:{} ) RETURN p.id,p.{}".format(endpoint, query),
        )

        print("member", endpoint, query)
        return self._data.show_data(get_data)

    def get_object_property(self, query):
        """
        Show the given type of property of given object.
        :param query: get query from the user,Ex:object</api/DroneCollection/2
        :return: get data from the Redis memory.
        """
        endpoint, query = query.split(" ")
        endpoint = endpoint.replace("object", "")
        index = endpoint.find("Collection")
        id_ = "object" + endpoint[5:index]
        get_data = self.connection.execute_command(
            "GRAPH.QUERY",
            "apidoc",
            'MATCH ( p:{}) WHERE (p.parent_id = "{}") RETURN p.{}'.format(
                id_, endpoint, query
            ),
        )

        print("object", endpoint, query)
        return self._data.show_data(get_data)


class ClassPropertiesValue:
    """
    ClassPropertiesValue is used for geting the values for properties of class
    And once values get from server and then it stored in Redis.
    """

    def __init__(self, api_doc, url, graph):
        self.redis_connection = RedisProxy()
        self.handle_data = HandleData()
        self.connection = self.redis_connection.get_connection()
        self._data = self.handle_data
        self.clas = ClassEndpoints(graph.redis_graph, graph.class_endpoints)

        self.api_doc = api_doc
        self.url = url

    def data_from_server(self, endpoint):
        """
        Load data from the server for once.
        :param endpoint: endpoint for getting data from the server.
        :return: get data from the Redis memory.
        """
        self.clas.load_from_server(
            endpoint, self.api_doc, self.url, self.connection)

        get_data = self.connection.execute_command(
            "GRAPH.QUERY",
            "apidoc",
            """MATCH(p:classes)
               WHERE(p.type='{}')
               RETURN p.property_value""".format(
                endpoint
            ),
        )
        return get_data

    def get_property_value(self, query):
        """
        Load data in Redis if data is not in it with help of checklist.
        Checklist have the track on endpoints.
        And access the properties values and show them.
        :param query: get query from the user, Ex:classLocation property_value
        :return: get data from the Redis memory.
        """
        query = query.replace("class", "")
        endpoint = query.replace(" property_value", "")
        if str.encode("fs:endpoints") in self.connection.keys() and str.encode(
            endpoint
        ) in self.connection.smembers("fs:endpoints"):
            get_data = self.connection.execute_command(
                "GRAPH.QUERY",
                "apidoc",
                """MATCH (p:classes)
                   WHERE (p.type = '{}')
                   RETURN p.property_value""".format(
                    endpoint
                ),
            )
        else:
            self.connection.sadd("fs:endpoints", endpoint)
            print(self.connection.smembers("fs:endpoints"))
            get_data = self.data_from_server(endpoint)

        print(endpoint, "property_value")
        return self._data.show_data(get_data)


class CompareProperties:
    """
    CompareProperties is used for extracting endpoints with help of properties
    Like input: name Drone1 and model xyz
    Then output: /api/DroneCollection/2
    With follows objects_property_comparison_list()
    """

    def __init__(self):
        self.redis_connection = RedisProxy()
        self.handle_data = HandleData()
        self.connection = self.redis_connection.get_connection()
        self._data = self.handle_data

    def faceted_key(self, key, value):
        """
        It is simply concatenate the arguments and make faceted key.
        """
        return "{}".format("fs:" + key + ":" + value)

    def convert_byte_string(self, value_set):
        """
        It converts byte strings to strings.
        """
        new_value_set = set()
        for obj in value_set:
            string = obj.decode("utf-8")
            new_value_set.add(string)
        return new_value_set

    def and_or_query(self, query_list):
        """
        It is a recursive function.
        It takes the arguement as list(query_list)
        which contains the faceted indexes and operation and brackets also.
        List Ex:['fs:model:xyz', 'and', '(', 'fs:name:Drone1', 'or',
                'fs:name:Drone2', ')']
                for query "model xyz and (name Drone1 or name Drone2)"
        :param query_list: get a list of faceted indexes and operations
        :param return: get data from the Redis memory for specific query.
        """
        # check if there is both "and" and "or" with help of bracket.
        if ")" not in query_list:
            # if only one operation "and" or "or".
            if "or" in query_list:
                while query_list.count("or") > 0:
                    query_list.remove("or")
                get_data = self.connection.sunion(*query_list)
                return get_data
            else:
                while query_list.count("and") > 0:
                    query_list.remove("and")
                get_data = self.connection.sinter(*query_list)
                return get_data
        else:
            # if both the operators are present in query
            for query_element in query_list:
                if query_element == ")":
                    # find index for closed bracket
                    close_index = query_list.index(query_element)
                    break
            for i in range(close_index, -1, -1):
                if query_list[i] == "(":
                    # find index for open bracket
                    open_index = i
                    break
            get_value = self.and_or_query(
                query_list[open_index + 1: close_index])
            get_value = self.convert_byte_string(get_value)

            # design random faceted key for store result of partial query.
            faceted_key = "fs:" + "".join(
                random.choice(string.ascii_letters + string.digits)
                for letter in range(8)
            )
            # add data in random faceted key.
            for obj in get_value:
                self.connection.sadd(faceted_key, obj)
            # add new executed partial query value with key in query list.
            query_list.insert(open_index, faceted_key)
            # generate new query after remove executed partial query
            query_list = (
                query_list[0: open_index + 1]
                + query_list[close_index + 2: len(query_list)]
            )
            return self.and_or_query(query_list)

    def object_property_comparison_list(self, query):
        """
        It takes the argument as a string that can contain many keys and value
        And make a list of all keys and values and identify operator(if there)
        And execute sinter or sunion commands of Redis over faceted keys.
        :param query: get query from the user, Ex: name Drone1
        :return: get data from the Redis memory.
        """

        faceted_list = []
        query_list = []
        while True:
            if query.count(" ") > 1:
                key, value, query = query.split(" ", 2)
                while "(" in key:
                    query_list.append("(")
                    key = key.replace("(", "", 1)

                faceted_list.append(self.faceted_key(key, value))
                query_list.append(
                    self.faceted_key(key.replace(
                        "(", ""), value.replace(")", ""))
                )
                while ")" in value:
                    query_list.append(")")
                    value = value.replace(")", "", 1)
            else:
                key, value = query.split(" ")
                query = ""
                while "(" in key:
                    query_list.append("(")
                    key = key.replace("(", "", 1)

                faceted_list.append(self.faceted_key(key, value))
                query_list.append(
                    self.faceted_key(key.replace(
                        "(", ""), value.replace(")", ""))
                )
                while ")" in value:
                    query_list.append(")")
                    value = value.replace(")", "", 1)
            if len(query) > 0:
                operation, query = query.split(" ", 1)
                query_list.append(operation)

            else:
                break

        get_data = self.and_or_query(query_list)
        return self.show_data(get_data)

    def show_data(self, get_data):
        """It returns the data in readable format."""
        property_list = []
        for string1 in get_data:
            string1 = string1.decode("utf-8")
            property_list.append(string1)
        #        print("list   ",property_list)
        return property_list


class QueryFacades:
    """
    It is used for call the above defined functions based on given query.
    Using test as a bool which identify that function is using for tests.
    """

    def __init__(self, api_doc, url, test):
        self.endpoint_query = EndPointQuery()
        self.api_doc = api_doc
        self.url = url
        self.properties = PropertiesQuery()
        self.compare = CompareProperties()
        self.test = test
        self.redis_connection = RedisProxy()
        self.connection = self.redis_connection.get_connection()

    def initialize(self, check_commit):
        """
        Initialize is used to initialize the graph for given URL.

        Initializes the mainGraph attribute
        """
        print("Initializing the graph...")

        self.graph = InitialGraph(self.url, self.api_doc)
        self.graph.main(check_commit)

    def check_fine_query(self, query):
        if query.count(" ") != 1:
            return RequestError("error")

    def user_query(self, query):
        """
        It calls function based on the query.

        """
        query = query.replace("show ", "")

        if query == "endpoints":
            self.endpoint_query.get_allEndpoints(query, self.graph)

        elif query == "classEndpoints":
            data = self.endpoint_query.get_classEndpoints(query, self.graph)
            return data

        elif query == "collectionEndpoints":
            data = self.endpoint_query.get_collectionEndpoints(
                query, self.graph)
            return data

        elif "members" in query:
            check_query = self.check_fine_query(query)
            if isinstance(check_query, RequestError):
                logger.info("Error: Incorrect query")
                return None
            else:
                self.members = CollectionMembersQuery(
                    self.api_doc, self.url, self.graph
                )
                if self.test:
                    data = self.members.data_from_server(
                        query.replace(" members", ""))
                    return data
                else:
                    data = self.members.get_members(query)
                    return data
        elif "objects" in query:
            if query[-1] == " ":
                logger.info("Error: incorrect query")
                return None
            check_query = self.check_fine_query(query)
            if isinstance(check_query, RequestError):
                logger.info("Error: Incorrect query")
                return None
            else:
                data = self.properties.get_members_properties(query)
                return data
        elif "object" in query:
            if query[-1] == " ":
                logger.info("Error: incorrect query")
                return None
            check_query = self.check_fine_query(query)
            if isinstance(check_query, RequestError):
                logger.info("Error: Incorrect query")
                return None
            else:
                data = self.properties.get_object_property(query)
                return data
        elif "Collection" in query:
            if query[-1] == " ":
                logger.info("Error: incorrect query")
                return None
            check_query = self.check_fine_query(query)
            if isinstance(check_query, RequestError):
                logger.info("Error: Incorrect query")
                return None
            else:
                data = self.properties.get_collection_properties(query)
                return data
        elif "class" in query and "property_value" in query:
            check_query = self.check_fine_query(query)
            if isinstance(check_query, RequestError):
                logger.info("Error: Incorrect query")
                return None
            else:
                self.class_property = ClassPropertiesValue(
                    self.api_doc, self.url, self.graph
                )
                data = self.class_property.get_property_value(query)
                return data
        elif "class" in query:
            if query[-1] == " ":
                logger.info("Error: incorrect query")
                return None
            check_query = self.check_fine_query(query)
            if isinstance(check_query, RequestError):
                logger.info("Error: Incorrect query")
                return None
            else:
                data = self.properties.get_classes_properties(query)
                return data
        else:
            if " and " in query or " or " in query:
                if query[-1] == " " or query[-3] == "and" or query[-2] == "or":
                    logger.info("Error: incorrect query")
                    return None
                query_len = len(query.split())
                and_or_count = query.count("and") + query.count("or")
                if query_len != (and_or_count + 2 * (and_or_count + 1)):
                    logger.info("Error: Incorrect query")
                    return None
                data = self.compare.object_property_comparison_list(query)
                return data
            elif query.count(" ") == 1:
                key, value = query.split(" ")
                print("query: ", query)
                search_index = "fs:" + key + ":" + value
                for key in self.connection.keys():
                    if search_index == key.decode("utf8"):
                        data = self.connection.smembers(key)
                        return data
            logger.info(
                "Incorrect query: Use 'help' to know about querying format")
            return None


def query(facades):
    """
    Used to query the API Documentation

    :param facades: Object used to query the API Docmentation. Instance of `QueryFacades`
    """

    while True:
        print("Press exit to quit.")
        query = input(">>>").strip()
        if query == "exit":
            print("Exiting. Bye bye...")
            return 0
        elif query == "help":
            help()
        else:
            facades.user_query(query)


def connect():
    """Prompts user for URL of the API and initializes a graph"""

    url = input(
        "Please input the address of the API you want to connect to -> "
    ).strip()

    url_response = HandleData().load_data(url + "/vocab")

    if isinstance(url_response, RequestError):
        print("\nInvalid URL. Please try again using 'connect' command\n")
    else:
        api_doc = create_doc(url_response)
        facades = QueryFacades(api_doc, url, False)
        check_url = str.encode(url)
        check_url_exist(check_url, facades)
        return facades


def main():
    """
    Main function

    Returns:
        Data returned from the query function.
    """

    facades = None
    # Prompt the user for a command and check the response
    while facades is None:
        command = input(">>>").strip().lower()
        if command == "exit":
            print("Exiting. Bye bye...")
            return 0
        elif command == "help":
            help()
            continue
        elif command == "connect":
            facades = connect()
        else:
            print("Invalid Command")
    return query(facades)


if __name__ == "__main__":
    main()
#    query = input()
#    query = query.replace("show ","")
#    operation_and_property_query(query)
#    endpoints_query(query)
#    class_endpoint_query("http://35.224.198.158:8080/api","classEndpoint")
