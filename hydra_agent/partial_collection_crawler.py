from requests import get


class PartialCollectionCrawler:
    """
    Crawler for Crawling Collections. 
    It can move forwards, backwards or can jump to specific page
    """

    def __init__(self, response):
        self.response = response
        self.base_url = 'http://localhost:8080'

    def initialize_forward(self):
        """
        Initializes the crawler to move forwards.
        :returns: Iterator
        """
        view = self.response['view']
        present_page = view['@id']
        while True:
            self.response = get(self.base_url + present_page).json()
            yield self.response['members']
            view = self.response['view']
            print('view')
            if 'next' in view:
                present_page = view['next']
            else:
                raise StopIteration("No more collection pages")

    def initialize_backward(self):
        """
        Initializes the crawler to move backwards.
        :returns: Iterator
        """
        view = self.response['view']
        present_page = view['@id']
        while True:
            self.response = get(self.base_url+present_page).json()
            yield self.response['members']
            view = self.response['view']
            if 'previous' in view:
                present_page = view['previous']
            else:
                raise StopIteration("No more collection pages")

    def jumpToPage(self, page):
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

    def jumpToLastPage(self):
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

    def totalItems(self):
        """returns total number of items of collection
        :return: Total number of items in collection
        """
        try:
            return self.response['totalItems']
        except KeyError:
            print("No totalItem provided")
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
