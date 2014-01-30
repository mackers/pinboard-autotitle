#!/usr/bin/env python

import pinboard
import sys
import requests
from bs4 import BeautifulSoup

p = pinboard.open(sys.argv[1], sys.argv[2])

posts = p.posts()

for post in posts:

    # {u'extended': u'', u'hash': u'1ab85941f250820b7cb25dccae71c3f0', u'description': u'', u'tags': [u'gis', u'maps', u'geo', u'python'], u'time_parsed': time.struct_time(tm_year=2014, tm_mon=1, tm_mday=29, tm_hour=20, tm_min=4, tm_sec=30, tm_wday=2, tm_yday=29, tm_isdst=-1), u'href': u'http://mapnik.org/', u'time': u'2014-01-29T20:04:30Z'}
    # print post

    changed = 0;

    print "Processing post: " + post['href']

    if post['description'] == '':
        try:
            h = requests.get(post['href'])
        except:
            print "  Unexpected error: ", sys.exc_info()[0]
            continue

        if not h.status_code == requests.codes.ok:
            print "  Got stauts " + str(h.status_code) + ", skipping"
            continue
        
        soup = BeautifulSoup(h.text)

        if soup.title and soup.title.string:
            post['description'] = soup.title.string
            print "  Got a title: " + unicode(post['description'])
        else:
            print "  Could not get title"
            post['description'] = post['href']
        
        changed = 1;
    else:
        print "  Title: " + post['description']

    if len(post['tags']) == 0 or (len(post['tags']) == 1 and post['tags'][0] == ''):
        r = p.suggest(post['href'])
        s = set(r['popular'] + r['recommended'])
        post['tags'] = list(s)

        if 'amazon' in post['href']:
            post['tags'] += ['amazon', 'books', 'toread']

        if '.gif' in post['href']:
            post['tags'] += ['gif']

        print "  Suggested tags: " + ', '.join(post['tags'])
        changed = 1;
    else:
        print "  Tags: " + ', '.join(post['tags'])

    if changed:
        print "  Saving post..."
        p.delete(url=post['href'])

        p.add(url=post['href'],
                description=post['description'],
                extended=post['extended'],
                tags=post['tags'])
        print "  ... done"
    else:
        print "  ... no change"

