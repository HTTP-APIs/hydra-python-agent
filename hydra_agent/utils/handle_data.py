import json
import logging
import urllib.request
from classes_objects import RequestError
from urllib.error import URLError, HTTPError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HandleData:
    """
    Used to fetch and print data.

    No public attributes.
    """
    @staticmethod
    def load_data(url: str):
        """
        Tries to fetch json from the url provided. Also handles the errors that may arise.

        Args:
            url(str): URL to the API Documentation.

        Returns:
            Data(Dict) if successful, RequestError otherwise.
        """

        try:
            with urllib.request.urlopen(url) as response:
                return json.loads(response.read().decode('utf-8'))
        except HTTPError as e:
            logger.info(f'Error code: {e.code}')
            return RequestError("error")
        except URLError as e:
            logger.info(f'Reason: {e.reason}')
            return RequestError("error")
        except ValueError as e:
            logger.info(f"Value Error: {e}")
            return RequestError("error")

    # def show_data(self, get_data):
    #     """
    #     Make the given data readable, because now it is in binary string form.
    #     Count is using for avoid stuffs like query internal execution time.
    #     :param get_data: data get from the Redis memory.
    #     """
    #     count = 0
    #     all_property_lists = []
    #     for objects in get_data:
    #         count += 1
    #         # Show data only for odd value of count.
    #         # because for even value it contains stuffs like time and etc.
    #         # ex: Redis provide data like if we query class endpoint
    #         # output like:
    #         # [[endpoints in byte object form],[query execution time:0.5ms]]
    #         # So with the help of count, byte object convert to string
    #         # and also show only useful strings not the query execution time.
    #         if count % 2 != 0:
    #             for obj1 in objects:
    #                 for obj in obj1:
    #                     string = obj.decode('utf-8')
    #                     map_string = map(str.strip, string.split(','))
    #                     property_list = list(map_string)
    #                     check = property_list.pop()
    #                     property_list.append(check.replace("\x00", ""))
    #                     if property_list[0] != "NULL":
    #                         #                        print(property_list)
    #                         all_property_lists.append(property_list)
    #     return all_property_lists
