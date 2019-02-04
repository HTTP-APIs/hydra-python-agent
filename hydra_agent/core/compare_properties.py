import string
import random
from core.utils.redis_proxy import RedisProxy
from core.utils.handle_data import HandleData


class CompareProperties:
    """
    CompareProperties is used for extracting endpoints with help of properties
    Like input: name Drone1 and model xyz
    Then output: /api/DroneCollection/2
    With follows objects_property_comparison_list()

    Attributes:
        connection: instance of redis-client
        _data: Instance of HandleData used to print data(To be changed soon)
    """

    def __init__(self):
        self.connection = RedisProxy.get_connection()
        self._data = HandleData()

    def faceted_key(self, key: str, value: str) -> str:
        """
        Concatenates the arguments and returns a faceted key
        """
        return "{}".format("fs:" + key + ":" + value)

    def convert_byte_string(self, value_set: set) -> set:
        """
        It converts byte strings to strings.
        """
        new_value_set = set()
        for obj in value_set:
            string = obj.decode("utf-8")
            new_value_set.add(string)
        return new_value_set

    def and_or_query(self, query_list: list) -> list:
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

    def object_property_comparison_list(self, query: str) -> list:
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

    def show_data(self, get_data: list) -> list:
        """It returns the data in readable format."""
        property_list = []
        for string1 in get_data:
            string1 = string1.decode("utf-8")
            property_list.append(string1)
        #        print("list   ",property_list)
        return property_list
