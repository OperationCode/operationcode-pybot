import requests
from bs4 import BeautifulSoup
import urllib

class SearchStockOverflow:

    def __init__(self, channel: str, user: str, input_text: str, app):
        self.channel_id = channel
        self.user_id = user
        self.input_text = self.remove_search(input_text)
        self.app = app

    def remove_search(self, initial_input):
        return initial_input.split("!search", 1)[1]


    async def return_links(self) -> dict:
        if not self.input_text:
            return {"message": {"text": self._default_error_message(), "channel": self.channel_id}}
        else:
            if self.input_text:
                links = _get_search_links(self.input_text)
                if (len(links)==0):
                    # No results found
                    response_message = "Sorry, couldn't find relevant links.\nCan you reformat the question?"
                else:
                    response_message = "Here are some StackOverflow links to help cater your doubts:\n\n"
                    for link in links:
                        response_message = response_message + link["text"] + "\n"
                        response_message = response_message + link["link"] + "\n\n"
                return {"message": response_message}

        return {"message": "Sorry, couldn't find relevant links.\nCan you reformat the question?"}

    def _default_error_message(self):
        return (
            "Please enter an appropriate search query.\n"\
            + "For example: !search how to print a line in Java."
        )

    def _get_search_links(self, query):
        """
        Takes in the doubt query and returns a dictionary of at max 5 query items.
        returning a list of dictionary of format {"text": <query_title>, "link": <query_link>}
        """
        params = urllib.parse.urlencode({'q': query, 'sort': 'relevance'})
        url = "https://stackoverflow.com/search?" + params
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'lxml')
        links = []
        result_count = 0
        for result in soup.findAll('div', attrs = {'class': 'result-link'}):
            query_link = ("https://stackoverflow.com/" + result.h3.a['href'])
            query_data = (result.h3.a.text)
            links.append({"text": str.strip(query_data), "link": query_link})
            result_count+=1
            if (result_count>=5):
                break
        return links