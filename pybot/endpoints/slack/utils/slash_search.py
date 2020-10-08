import requests
from bs4 import BeautifulSoup
import urllib

def get_search_links(query):
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