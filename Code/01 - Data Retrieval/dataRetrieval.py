
import os
import sys

import itertools
import github3
import dataset

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

def user_to_dict(user):
    return dict(
        id       = user.id,
        login    = user.login,
        name     = user.name,
        location = user.location,
        company  = user.company
    )

db = dataset.connect('sqlite:///database.db')

users_table     = db['users']
followers_table = db['followers']
following_table = db['following']

def insert_user(user):
    user_dict = user_to_dict(user)
    followers = [f for f in user.followers()]
    following = [f for f in user.following()]

    users_table.insert(user_dict)
    for f in followers:
        followers_table.insert(dict(user_id=user.id, follower_id=f.id))

    for f in following:
        following_table.insert(dict(user_id=user.id, following_id=f.id))

for res in search_res:
    print('Processing user {}'.format(res.user.login))
    user = res.user.refresh()
    insert_user(user)

