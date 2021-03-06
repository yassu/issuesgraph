#!/usr/bin/env python

import re
import os
import sys
import cPickle as pickle
import requests
from collections import namedtuple


Issue = namedtuple('Issue',
                   ['number', 'url', 'state', 'created_at', 'closed_at'])


def paginate(query):
    headers = {}
    if 'GITHUB_ACCESSTOKEN' in os.environ:
        access_token = os.environ['GITHUB_ACCESSTOKEN']
        headers['Authorization'] = 'token %s' % access_token

    response = requests.get(query, headers=headers)
    print('Now fetching %s...' % query)
    yield response

    while response.status_code == 200:
        matched = re.match('<(.*?)>; rel="next"',
                           response.headers.get('link', ''))
        if not matched:
            break
        else:
            next_url = matched.group(1)
            print('Now fetching %s...' % next_url)
            response = requests.get(next_url, headers=headers)
            yield response


def print_usage():
    print("fetch.py [username/repo]")


def main(args):
    if len(args) != 2:
        print_usage()
        return -1

    baseurl = "https://api.github.com/repos/%s/issues" % args[-1]

    fetched = []
    query = baseurl + "?state=all"
    for response in paginate(query):
        assert response.status_code == 200
        issues = response.json()
        for item in issues:
            issue = Issue(int(item['number']), item['url'], item['state'],
                          item['created_at'], item.get('closed_at'))
            fetched.append(issue)

    with open('issues.dat', 'wb') as f:
        pickle.dump(fetched, f)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
