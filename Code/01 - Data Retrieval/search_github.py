
import os
import sys
import time
import datetime

import itertools
import github3

from utils import *

def location(loc):
    return 'location:{}'.format(loc)

def search_users(db, query, count=-1):
    key  = 'search_users:{}'.format(query)
    gen  = gh.search_users(query, number=count, sort='followers', etag=etag(db, key))

    return gen_to_list(db, gen, key)

if __name__ == '__main__':

    db = get_mongo_db()
    gh = github_login()

    show_rate_limit(gh)

    locations = ['Switzerland', 'Suisse', 'Schweiz', 'Svizzera', 'CH']

    users = []

    for loc in locations:
        print('Searching for users in \'{}\'...'.format(loc))
        loc_users = search_users(db, location(loc))
        print('=> Found {} users.'.format(len(loc_users)))
        users.extend(loc_users)

    for res in users:
        insert_user(db, res.user, in_ch=True)

