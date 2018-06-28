import redis
import hydra_graph as graph
import urllib.request
import json
from hydrus.hydraspec import doc_maker
from urllib.error import URLError, HTTPError
from collections_endpoint import CollectionEndpoints
from classes_objects import ClassEndpoints


class HandleData:
    """
    Handle data is used to play with data.
    It have two functions load_data and show_data.
    Work of load_data is to fetch the data from server and
    Work of show_data is to show the data of Redis in readable format.
    """

    def load_data(self, url):
        """
        Load the data for the given url and return it.
        Also handle with the HTTPError, it prints the error
        """
        try:
            response = urllib.request.urlopen(url)
        except HTTPError as e:
            print('Error code: ', e.code)
            return ("error")
        except URLError as e:
            print('Reason: ', e.reason)
            return ("error")
        else:
            return json.loads(response.read().decode('utf-8'))

    def show_data(self, get_data):
        """
        Make the given data readable, because now it is in binary string form.
        Count is using for avoid stuffs like query internal execution time.
        """
        count = 0
        for objects in get_data:
            count += 1
            if count % 2 != 0:
                for obj in objects:
                    string = obj.decode('utf-8')
                    map_string = map(str.strip, string.split(','))
                    property_list = list(map_string)
                    check = property_list.pop()
                    property_list.append(check.replace("\x00", ""))
                    print(property_list)


class RedisProxy:
    """
    RedisProxy is used for make a connection to the Redis.
    """

    def __init__(self):
        self.connection = redis.StrictRedis(host='localhost', port=6379, db=0)

    def get_connection(self):
        return self.connection


class EndpointQuery:
    """
    EndpointQuery is used for get the endpoints from the Redis.
    """

    def __init__(self):
        self.redis_connection = RedisProxy()
        self.handle_data = HandleData()
        self.connection = self.redis_connection.get_connection()
        self._data = self.handle_data

    def get_allEndpoints(self, query):
        """
        It will return both type(class and collection) of endpoints.
        """
        get_data = self.connection.execute_command(
            'GRAPH.QUERY',
            'apidoc',
            "MATCH (p:classes) RETURN p") + self.connection.execute_command(
            'GRAPH.QUERY',
            'apidoc',
            "MATCH (p:collection) RETURN p")
        print("classEndpoints + CollectionEndpoints")

        return self._data.show_data(get_data)

    def get_classEndpoints(self, query):
        """
        It will return all class Endpoints.
        """
        get_data = self.connection.execute_command(
            'GRAPH.QUERY', 'apidoc', "MATCH (p:classes) RETURN p")

        print("classEndpoints")

        return self._data.show_data(get_data)

    def get_collectionEndpoints(self, query):
        """
        It will returns all collection Endpoints.
        """
        get_data = self.connection.execute_command(
            'GRAPH.QUERY', 'apidoc', "MATCH (p:collection) RETURN p")

        print("collectoinEndpoints")

        return self._data.show_data(get_data)


class CollectionmembersQuery:
    """
    CollectionmembersQuery is used for get members of any collectionendpoint.
    Once it get the data from the server and store it in Redis.
    And after that it can query from Redis memory.
    Check_list is using for track which collection endpoint data is in Redis.
    """

    def __init__(self, api_doc, url):
        self.redis_connection = RedisProxy()
        self.handle_data = HandleData()
        self.connection = self.redis_connection.get_connection()
        self._data = self.handle_data
        self.collect = CollectionEndpoints(graph.redis_graph,
                                           graph.class_endpoints)

        self.api_doc = api_doc
        self.url = url

    def data_from_server(self, endpoint):
        """
        Load data from the server for first time.
        """
        self.collect.load_from_server(endpoint,
                                      self.api_doc,
                                      self.url,
                                      self.connection)

        get_data = self.connection.execute_command(
            'GRAPH.QUERY',
            'apidoc',
            'MATCH(p:collection) WHERE(p.type="{}") RETURN p.members'.format(
                endpoint))
        return get_data

    def get_members(self, query):
        """
        Gets Data from the Redis.
        """
        endpoint = query.replace(" members", "")
        print(check_list)
        if endpoint in check_list:
            get_data = self.connection.execute_command(
                'GRAPH.QUERY',
                'apidoc',
                """MATCH(p:collection)
                   WHERE(p.type='{}')
                   RETURN p.members""".format(
                    endpoint))

        else:
            check_list.append(endpoint)
            print(check_list)
            get_data = self.data_from_server(endpoint)

        print(endpoint, " members")
        return self._data.show_data(get_data)


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
        """
        query = query.replace("class", "")
        endpoint, query = query.split(" ")
        get_data = self.connection.execute_command(
            'GRAPH.QUERY',
            'apidoc',
            'MATCH ( p:classes ) WHERE (p.type="{}") RETURN p.{}'.format(
                endpoint,
                query))
        print("class", endpoint, query)
        return self._data.show_data(get_data)

    def get_collection_properties(self, query):
        """
        Show the given type of property of given collection endpoint.
        """
        endpoint, query = query.split(" ")

        get_data = self.connection.execute_command(
            'GRAPH.QUERY',
            'apidoc',
            'MATCH ( p:collection ) WHERE (p.type="{}") RETURN p.{}'.format(
                endpoint,
                query))

        print("collection", endpoint, query)
        return self._data.show_data(get_data)

    def get_members_properties(self, query):
        """
        Show the given type of property of given member.
        """
        endpoint, query = query.split(" ")
        get_data = self.connection.execute_command(
            'GRAPH.QUERY',
            'apidoc',
            'MATCH ( p:{} ) RETURN p.id,p.{}'.format(
                endpoint,
                query))

        print("member", endpoint, query)
        return self._data.show_data(get_data)

    def get_object_property(self, query):
        """
        Show the given type of property of given object.
        """
        endpoint, query = query.split(" ")
        endpoint = endpoint.replace("object", "")
        index = endpoint.find("Collection")
        id_ = "object" + endpoint[5:index]
        print(id_, endpoint)
        get_data = self.connection.execute_command(
            'GRAPH.QUERY',
            'apidoc',
            'MATCH ( p:{}) WHERE (p.parent_id = "{}") RETURN p.{}'.format(
                id_,
                endpoint,
                query))

        print("object", endpoint, query)
        return self._data.show_data(get_data)


class ClassPropertiesValue:
    """
    ClassPropertiesValue is used for geting the values for properties of class
    And once values get from server and then it stored in Redis.
    """

    def __init__(self, api_doc, url):
        self.redis_connection = RedisProxy()
        self.handle_data = HandleData()
        self.connection = self.redis_connection.get_connection()
        self._data = self.handle_data
        self.clas = ClassEndpoints(graph.redis_graph,
                                   graph.class_endpoints)

        self.api_doc = api_doc
        self.url = url

    def data_from_server(self, endpoint):
        """
        Load data from the server for once.
        """
        self.clas.load_from_server(endpoint,
                                   self.api_doc,
                                   self.url,
                                   self.connection)

        get_data = self.connection.execute_command(
            'GRAPH.QUERY',
            'apidoc',
            """MATCH(p:classes)
               WHERE(p.type='{}')
               RETURN p.property_value""".format(
                endpoint))
        return get_data

    def get_property_value(self, query):
        """
        Load data in Redis if data is not in it with help of checklist.
        Checklist have the track on endpoints.
        And access the properties values and show them.
        """
        query = query.replace("class", "")
        endpoint = query.replace(" property_value", "")
        print(check_list)
        if endpoint in check_list:
            get_data = self.connection.execute_command(
                'GRAPH.QUERY',
                'apidoc',
                """MATCH (p:classes)
                   WHERE (p.type = '{}')
                   RETURN p.property_value""".format(
                    endpoint))
        else:
            check_list.append(endpoint)
            print(check_list)
            get_data = self.data_from_server(endpoint)

        print(endpoint, "property_value")
        return self._data.show_data(get_data)


class CompareProperties:
    """
    CompareProperties is used for extracting endpoints with help of properties
    Like input: name Drone1 and model xyz
    then output: /api/DroneCollection/2
    with follows objects_property_comparison_list()
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
        return ("{}".format("fs:" + key + ":" + value))

    def object_property_comparison_list(self, query):
        """
        It takes the argument as a string that can contain many keys and value
        And make a list of all keys and values and identify operator(if there)
        And execute sinter or sunion commands of Redis over faceted keys.
        """
        union = 0
        faceted_list = []
        while(1):
            if query.count(" ") > 1:
                key, value, query = query.split(" ", 2)
                faceted_list.append(self.faceted_key(key, value))
            else:
                key, value = query.split(" ")
                query = ""
                faceted_list.append(self.faceted_key(key, value))
            if len(query) > 0:
                operation, query = query.split(" ", 1)
                if operation == "or":
                    union = 1

            else:
                break
        if union == 1:
            get_data = self.connection.sunion(*faceted_list)
            print(get_data)
        else:
            get_data = self.connection.sinter(*faceted_list)
            print(get_data)


class QueryFacades:
    """
    It is used for call the above defined functions based on given query.
    """

    def __init__(self, api_doc, url):

        self.endpoint_query = EndpointQuery()
        self.api_doc = api_doc
        self.url = url
        self.properties = PropertiesQuery()
        self.compare = CompareProperties()

    def initialize(self):
        """
        Initialize is used to initialize the graph for given url.
        """
        print("just initialize")

        graph.main(self.url, self.api_doc)

    def user_query(self, query):
        """
        It calls function based on queries type.
        """
        query = query.replace("show ", "")
        if query == "endpoints":
            self.endpoint_query.get_allEndpoints(query)
        elif query == "classEndpoints":
            self.endpoint_query.get_classEndpoints(query)
        elif query == "collectionEndpoints":
            self.endpoint_query.get_collectionEndpoints(query)
        elif "members" in query:
            self.members = CollectionmembersQuery(self.api_doc, self.url)
            self.members.get_members(query)
        elif "objects" in query:
            self.properties.get_members_properties(query)
        elif "object" in query:
            self.properties.get_object_property(query)
        elif "Collection" in query:
            self.properties.get_collection_properties(query)
        elif "class" in query and "property_value" in query:
            self.class_property = ClassPropertiesValue(self.api_doc, self.url)
            self.class_property.get_property_value(query)
        elif "class" in query:
            self.properties.get_classes_properties(query)
        else:
            self.compare.object_property_comparison_list(query)


def main():
    """
    Take URL as an input and make graph using initilize function.
    Querying still user wants or still user enters the exit.
    """
    url = input("url>>>")
    handle_data = HandleData()
    apidoc = handle_data.load_data(url + "/vocab")
    while (1):
        if apidoc == "error":
            print("enter right url")
            url = input("url>>>")
            apidoc = handle_data.load_data(url + "/vocab")
        else:
            break

    api_doc = doc_maker.create_doc(apidoc)
    facades = QueryFacades(api_doc, url)
    facades.initialize()
    global check_list
    check_list = []
    while(1):
        print("press exit to quit")
        query = input(">>>")
        if query == "exit":
            break
        else:
            facades.user_query(query)


if __name__ == "__main__":
    print("querying format")
    print("for endpoint:- show endpoint")
    print("for class_endpoint:- show classEndpoint")
    print("for collection_endpoint:- show collectionEndpoint")
    print("for members of collection_endpoint:-",
          "show <collection_endpoint> members")
    print("for properties of any member:-",
          "show object<id_of_member> properties ")
    print("for properties of objects:- show objects<endpoint> properties")
    print("for collection properties:-",
          "show <collection_endpoint> properties")
    print("for classes properties:- show class<class_endpoint> properties")
    print("for compare properties:-show <key> <value> and/or <key1> <value1>")
    main()
#    query = input()
#    query = query.replace("show ","")
#    operation_and_property_query(query)
# endpoints_query(query)
#    class_endpoint_query("http://35.224.198.158:8080/api","classEndpoint")