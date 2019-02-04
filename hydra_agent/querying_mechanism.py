import logging
from core.utils.help import help
from typing import Tuple
from hydra_graph import InitialGraph
from redisgraph.query_result import QueryResult
from hydra_python_core.doc_maker import HydraDoc
from core.utils.redis_proxy import RedisProxy
from core.utils.handle_data import HandleData
from core.end_point_query import EndPointQuery
from core.utils.check_url import check_url_exist
from core.properties_query import PropertiesQuery
from hydra_python_core.doc_maker import create_doc
from core.utils.classes_objects import RequestError
from core.compare_properties import CompareProperties
from core.class_properties import ClassPropertiesValue
from core.collection_member_query import CollectionMembersQuery

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryFacades:
    """
    It is used to filter query type

    Attributes:
        api_doc: HydraDoc object for the API Documentation
        url: URL for the API Documentation
        connection: An instance of redis-client
    """

    def __init__(self, api_doc: HydraDoc, url: str, test: bool):
        self.api_doc = api_doc
        self.url = url
        self.test = test
        self.connection = RedisProxy.get_connection()

    def initializeQueries(self):
        """
        Creates instance of various classes used for different type of queries
        """
        self.compare = CompareProperties()
        self.properties = PropertiesQuery(self.graph)
        self.endpoint_query = EndPointQuery(self.graph)
        self.members = CollectionMembersQuery(
            self.api_doc, self.url, self.graph)
        self.class_property = ClassPropertiesValue(
            self.api_doc, self.url, self.graph
        )

    def initialize(self, check_commit: bool):
        """
        Initialize is used to initialize the graph for given URL.

        Args:
            check_commit: Boolean to check if URL is already registered in redis or not
        """

        self.graph = InitialGraph(self.url, self.api_doc)
        self.graph.main(check_commit)
        self.initializeQueries()

    def check_fine_query(self, query: str) -> Tuple[None, RequestError]:
        if query.count(" ") != 1:
            return RequestError("error")

    def user_query(self, query: str) -> QueryResult:
        """
        It calls function based on the query.

        Args:
            query: Input query from the user
        """
        query = query.replace("show ", "")

        if query == "endpoints":
            self.endpoint_query.get_allEndpoints(query)

        elif query == "classEndpoints":
            data = self.endpoint_query.get_classEndpoints(query)
            return data

        elif query == "collectionEndpoints":
            data = self.endpoint_query.get_collectionEndpoints(
                query)
            return data

        elif "members" in query:
            check_query = self.check_fine_query(query)
            if isinstance(check_query, RequestError):
                logger.info("Error: Incorrect query")
                return None
            else:
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
                data = self.properties.get_members_properties(
                    query)
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
                data = self.properties.get_collection_properties(
                    query)
                return data
        elif "class" in query and "property_value" in query:
            check_query = self.check_fine_query(query)
            if isinstance(check_query, RequestError):
                logger.info("Error: Incorrect query")
                return None
            else:
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
                data = self.properties.get_classes_properties(
                    query)
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


def query(facades: QueryFacades) -> QueryResult:
    """
    Used to query the API Documentation

    Args:
        facades: Instace of QueryFacades used to filter query types
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


def connect() -> QueryFacades:
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


def main() -> QueryResult:
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
