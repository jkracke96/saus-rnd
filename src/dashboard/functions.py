import requests
from bs4 import BeautifulSoup


def get_text_from_url(url):
    response = requests.get(url)
    html_text = response.text
    soup = BeautifulSoup(html_text, 'html.parser')
    text = soup.get_text()
    title = soup.title.string if soup.title else 'No title found'
    return {'text': text, 'title': title}
