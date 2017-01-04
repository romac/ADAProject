
import re
import sys
import json
import requests

from bs4 import BeautifulSoup
from utils import eprint

base_url = 'http://git-awards.com/users?type=country&country=Switzerland'

def get_page(url, **params):
    r = requests.get(url, params)

    if r.status_code is not requests.codes.ok:
        eprint('Something went wrong. Got status code = %d' % r.status_code)
        return None

    html = r.text

    return BeautifulSoup(html, 'html.parser')

def list_languages(page):
    opts = page.find(id='language').find_all('option')
    langs = [str(opt['value']) for opt in opts]

    return langs

def get_last_page_number(page):
    pagination = page.find(attrs={ 'class': 'pagination' })
    childs = pagination.find_all('li')
    last = childs[-1]
    link = last.find('a')
    url = link['href']
    match = re.match(r'''.*page=(\d+).*''', url)

    return int(match.group(1))

def list_users(page):
    users = page.find_all('td', attrs={ 'class': 'username' })

    return [str(user.string) for user in users]

def fetch_users_by_lang(lang):
    eprint('Fetching language {}...'.format(lang))
    page = get_page(base_url, language=lang)
    last_page_num = get_last_page_number(page)

    eprint(' => Found {} pages for {}'.format(last_page_num, lang))

    res = set([])

    for page_num in range(1, last_page_num + 1):
        eprint('Fetching page {}...'.format(page_num))
        page = get_page(base_url, language=lang, page=page_num)

        users = list_users(page)

        eprint(' => Got {} new users.'.format(len(users)))
        eprint(users)
        eprint()

        res.update(set(users))

    return res

page  = get_page(base_url)

langs = list_languages(page)
users = set([])

for lang in langs:
    users.update(fetch_users_by_lang(lang))

eprint('Found {} users.'.format(len(users)))

print(json.dumps(list(users)))

