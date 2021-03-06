import requests
import json
import re
import datetime
from collections import Counter
from collections import OrderedDict

url_base = 'https://wordpress.org/plugins'
url_el = '/wp-json/wp/v2/posts/?per_page='
op = []
posts = []
requires = []
tested = []
requires_php = []
downloads = []
installs = []
dates = []
per_page = 100
wp_current = '5.2'


def validation(val):
    if re.search(r"\d", val):
        o = re.search(r"\d(.\d)?(.\d)?", val)
        o = o.group()

        if re.search(r"\d\d", o):
            return False
        if re.search(r"/", o):
            o = o.replace("/", ".")
        if re.search(r" ", o):
            o = o.replace(" ", ".")
        if re.search(r",", o):
            o = o.replace(",", ".")
        if re.fullmatch(r"\d", o):
            o = o + '.0'
        if re.fullmatch(r"\d.\d.\d", o):
            o = re.search(r"\d.\d", o)
            o = o.group()

        if o > wp_current:
            return False

        return (o)

    else:
        return False


def val_php(val):
    if re.search(r"\d", val):
        o = re.search(r"\d(.\d)?(.\d)?", val)
        o = o.group()

        if re.search(r"\d\d", o):
            return False
        if re.search(r"/", o):
            o = o.replace("/", ".")
        if re.search(r",", o):
            o = o.replace(",", ".")
        if re.fullmatch(r"\d", o):
            o = o + '.0'
        if re.fullmatch(r"\d.\d.\d", o):
            o = re.search(r"\d.\d", o)
            o = o.group()

        return (o)

    else:
        return False


def dl_counter(val):
    if 0 <= val < 100:
        o = '0-99'
    elif 100 < val < 1000:
        o = '100-999'
    elif 1000 < val < 10000:
        o = '1000-9999'
    elif 10000 < val < 100000:
        o = '10k-99k'
    elif 100000 < val:
        o = '100k+'
    else:
        return False

    return o


def rel_time(val):
    cur_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    cur_time = datetime.datetime.strptime(cur_time, '%Y-%m-%d %H:%M:%S')
    try:
        val = datetime.datetime.strptime(val, '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        return False

    val = cur_time - val
    val = val.days

    if 0 <= val < 30:
        o = '0'

    elif 30 < val < 90:
        o = '1'

    elif 90 < val < 180:
        o = '2'

    elif 180 < val < 365:
        o = '3'

    elif 365 < val < 730:
        o = '4'

    elif 730 < val < 1460:
        o = '5'

    elif 1460 < val:
        o = '6'

    else:
        return False

    return o


r = requests.get(url_base + url_el + str(per_page))
total_pages = int(r.headers['x-wp-totalpages'])
total = int(r.headers['x-wp-total'])
total_pages += 1

for i in range(1, total_pages):
    url = url_base + url_el + str(per_page) + '&page=' + str(i)
    r = requests.get(url)
    data = r.json()
    posts.append(data)

for post in posts:
    for li in post:
        di = dict(li)

        req = validation(di['meta']['requires'])
        tes = validation(di['meta']['tested'])
        php = val_php(di['meta']['requires_php'])
        dl = dl_counter(di['meta']['downloads'])
        ins = dl_counter(di['meta']['active_installs'])
        time = rel_time(di['modified'])

        if req:
            requires.append(req)

        if tes:
            tested.append(tes)

        if php:
            requires_php.append(php)

        if dl:
            downloads.append(dl)

        if ins:
            installs.append(ins)

        if time:
            dates.append(time)

# Count each dict
requires = Counter(requires)
tested = Counter(tested)
requires_php = Counter(requires_php)
downloads = Counter(downloads)
installs = Counter(installs)
dates = Counter(dates)

# Sort the dict
requires = OrderedDict(sorted(requires.items()))
tested = OrderedDict(sorted(tested.items()))
requires_php = OrderedDict(sorted(requires_php.items()))
dates = OrderedDict(sorted(dates.items()))

# Rename the dict dates
dates['Within a month ago'] = dates.pop('0')
dates['1 month ago'] = dates.pop('1')
dates['3 months ago'] = dates.pop('2')
dates['6 months ago'] = dates.pop('3')
dates['1 year ago'] = dates.pop('4')
dates['2 years ago'] = dates.pop('5')
dates['4 years ago'] = dates.pop('6')

# Make the list to dict
requires = dict(requires)
tested = dict(tested)
requires_php = dict(requires_php)
downloads = dict(downloads)
installs = dict(installs)
dates = dict(dates)

cur_time = datetime.datetime.utcnow().strftime('%Y,%m,%d,%H,%M,%S')

plugins = [requires, tested, requires_php, downloads, installs, dates,
           total, cur_time]

with open('plugins.json', 'w') as fp:
    json.dump(plugins, fp, separators=(',', ':'))
