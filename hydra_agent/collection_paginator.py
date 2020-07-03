from requests import get
import json


class Paginator:
    """
    Paginator for moving through Partial collections. 
    It can move forwards, backwards or can jump to specific page
    """

    def __init__(self, response, base_url='http://localhost:8080'):
        self.response = response
        self.base_url = base_url

    def initialize_forward(self):
        """
        Initializes the paginator to move forwards.
        :returns: Iterator
        """
        view = self.response['view']
        present_page = view['@id']
        yield_page = {"pages_ahead": True}
        while True:
            self.response = get(self.base_url + present_page).json()
            yield_page['members'] = self.response['members']
            if 'last' in view and view['last'] == present_page:
                yield_page['pages_ahead'] = False
            yield yield_page
            view = self.response['view']
            if 'next' in view:
                yield_page['pages_ahead'] = True
                present_page = view['next']
            else:
                yield_page['members'] = self.response['members']
                yield yield_page

    def initialize_backward(self):
        """
        Initializes the pagintor to move backwards.
        :returns: Iterator
        """
        view = self.response['view']
        present_page = view['@id']
        yield_page = {"pages_behind": False}
        while True:
            self.response = get(self.base_url+present_page).json()
            yield_page['members'] = self.response['members']
            if 'first' in view and view['first'] == present_page:
                yield_page['pages_behind'] = False
            yield yield_page
            view = self.response['view']
            if 'previous' in view:
                yield_page['pages_behind'] = True
                present_page = view['previous']
            else:
                yield_page['members'] = self.response['members']
                yield yield_page

    def jump_to_page(self, page):
        """
        Jumps to a specified page. 
        :params page: Page number to jump
        :returns members: Members of collection of that page.
        """
        try:
            url = self.base_url + self.response['@id'] + '?page=' + str(page)
            response = get(url).json()
            return response['members']
        except KeyError:
            print('No such page exists.')
            raise

    def jump_to_last_page(self):
        """
        Jumps to Last page of Collection
        :returns members of last page of Partial Collection
        """
        try:
            url = self.base_url + self.response['view']['last']
            response = get(url).json()
            return response['members']
        except KeyError:
            print("No last item in view")
            raise

    def total_items(self):
        """returns total number of items of collection
        :return: Total number of items in collection
        """
        try:
            return self.response['totalItems']
        except KeyError:
            print("No totalItem key provided")
            raise

    def total_pages(self):
        """
        Returns total Number of pages in the Collection
        :returns: total number of pages in the Partial Collection
        """
        try:
            last_page_url = self.response['view']['last']
            indexPage = last_page_url.index("page=")
            return last_page_url[indexPage + 5]
        except KeyError:
            print("Unable to find last page")
            raise
