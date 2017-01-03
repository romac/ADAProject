
import os
import sys

import itertools
import github3

from pymongo import MongoClient

GITHUB3_TOKEN = 'GITHUB3_TOKEN'
token = os.environ.get(GITHUB3_TOKEN)

if not token:
    print('Missing ' + GITHUB3_TOKEN + ' environment variable. Please check README.md.')
    sys.exit(1)

gh = github3.login(token=token)

def location(loc):
    return 'location:{}'.format(loc)

def search_users(query):
    return gh.search_users(query, number=10)

# TODO: Search also by major cities names

en_users = search_users(location('Switzerland'))
fr_users = search_users(location('Suisse'))
de_users = search_users(location('Schweiz'))
it_users = search_users(location('Svizzera'))
ch_users = search_users(location('CH'))

search_res = itertools.chain(en_users, fr_users, de_users, it_users, ch_users)

def user_to_dict(user, fetch_follow=False):
    if fetch_follow:
        followers = list(user.followers())
        following = list(user.following())
    else:
        followers = following = []

    followers_ids = [f.id for f in followers]
    following_ids = [f.id for f in following]

    user_dict = dict(
        _id       = user.id,
        login     = user.login,
        name      = user.name,
        location  = user.location,
        company   = user.company,
        followers = followers_ids,
        following = following_ids
    )

    return (user_dict, followers, following)

def insert_user(user, insert_follow=False):
    print('{}Refreshing user {}...'.format('' if insert_follow else '    ', user.login))
    user = user.refresh()

    (user_dict, followers, following) = user_to_dict(user, insert_follow)

    print('{}Inserting user {}...'.format('' if insert_follow else '    ', user.login))
    db.users.replace_one({ '_id': user_dict['_id'] }, user_dict, upsert=True)

    # if insert_follow:
    #     for f in followers:
    #         insert_user(f, False)

    #     for f in following:
    #         insert_user(f, False)

client = MongoClient('localhost', 27017)
db = client.ada

for res in search_res:
    print('Processing user {}...'.format(res.user.login))
    insert_user(res.user, True)

