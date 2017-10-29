import requests
import json
import re
from collections import Counter

url_base = 'https://wordpress.org/plugins'
op = []
posts = []
requires = []
tested = []
requires_php = []
per_page = 100


def validation(val):
    if re.search(r"\d", val):
        o = re.search(r"\d(.\d)?(.\d)?", val)
        o = o.group()

        if re.fullmatch(r"\d", o):
            o = o + '.0'

        if re.fullmatch(r"\d.\d.\d", o):
            o = re.search(r"\d.\d", o)
            o = o.group()

        return (o)

    else:
        return False

r = requests.get(url_base + '/wp-json/wp/v2/posts/?per_page=' + str(per_page))
total_pages = int(r.headers['x-wp-totalpages'])
total_pages += 1

for i in range(1, total_pages):
    url = url_base + '/wp-json/wp/v2/posts/?per_page=' + str(per_page) + '&page=' + str(i)
    r = requests.get(url)
    data = r.json()
    posts.append(data)

for post in posts:
    for li in post:
        di = dict(li)

        req = validation(di['meta']['requires'])
        tes = validation(di['meta']['tested'])
        php = validation(di['meta']['requires_php'])

        if req:
            requires.append(req)

        if tes:
            tested.append(tes)

        if php:
            requires_php.append(php)

requires = Counter(requires)
tested = Counter(tested)
requires_php = Counter(requires_php)

plugins = [requires, tested, requires_php]

with open('plugins.json', 'w') as fp:
    json.dump(plugins, fp)
