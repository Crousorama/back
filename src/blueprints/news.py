from flask import Blueprint, jsonify, request
import requests
from bs4 import BeautifulSoup

news_blueprint = Blueprint('news', __name__)


@news_blueprint.route('')
def get_news():
    """
    get news
    :return: dict {
        img: str,
        url: str,
        title: str,
        summary: str,
        publication_date: str
    }
    """
    news = []
    page = request.args.get('page') or 1
    r = requests.get('https://www.boursedirect.fr/fr/actualites/timeline/flux/aujourdhui/{}/undefined'.format(page))
    html = r.text
    soup = BeautifulSoup(html)
    articles = soup.findAll('div', {'class': 'timeline-heading'})
    for a in articles:
        a_soup = BeautifulSoup(str(a))
        day = a_soup.find('span', {'class': 'publishDay'}).text
        month = a_soup.find('span', {'class': 'text-muted'}).text
        hour = a_soup.find('span', {'class': 'publishHour'}).text
        date = '{} {} - {}'.format(day, month, hour)
        news.append({
            'img': 'https://www.boursedirect.fr' + a_soup.find('img').attrs['src'],
            'publication_date': date,
            'url': 'https://www.boursedirect.fr/' + a_soup.find('a').attrs['href'],
            'title': a_soup.find('h2', {'class': 'timeline-title'}).text,
            'summary': a_soup.findAll('p')[1].text,
        })
    return jsonify(news), 200


def find_publish_date(contents):
    for content in contents:
        if type(content) == 'str':
            return content.next
        if content.contents is None:
            pass
        return find_publish_date(content.contents)


@news_blueprint.route('/realtime')
def get_realtime_news():
    r = requests.get('https://investir.lesechos.fr/index.php')
    soup = BeautifulSoup(r.text)
    realtime_container = soup.find("div", {"class": "contenu-dernieres-infos"})
    news_links = realtime_container.findAllNext("a")
    news = []
    for n in news_links:
        try:
            tmp_n = {
                'date': n.contents[1].attrs['datetime'],
                'title': clean(n.contents[5].text)
            }
            news.append(tmp_n)
        except IndexError:
            continue
        except KeyError:
            continue
    return jsonify(news), 200


def clean(string):
    tmp = string.replace('\t', '').replace('\r', '').replace('\n', '').split('                             ')[0]
    if len(tmp.split('Conseil Investir')) > 1:
        tmp = tmp.split('Conseil Investir')[1]
    if len(tmp.split('Les recos des analystes :')) > 1:
        tmp = tmp.split('Les recos des analystes :')[1]
    return tmp


def clean_url(string: str):
    return string.replace("amp;", "")
