
import os
import sys
import time
import datetime

import itertools
import github3

from pymongo import MongoClient

from utils import *

def gen_to_list(gen, key, *args):
    values = list(gen)
    key    = key.format(*args)
    etag   = dict(key = key, etag = gen.etag)

    db.etags.replace_one({ 'key': key }, etag, upsert=True)

    return values

def etag(key, *args):
    doc = db.etags.find_one({ 'key': key.format(*args) })

    if doc is None:
        return None

    return doc['etag']

def location(loc):
    return 'location:{}'.format(loc)

def search_users(query, count=10):
    print('Searching for users: \'{}\'...'.format(query))

    key  = 'search_users:{}'.format(query)
    gen  = gh.search_users(query, number=count, etag=etag(key))

    return gen_to_list(gen, key)

def fetch_user(user, in_ch=False, fetch_props=None):
    if fetch_props is None:
        fetch_props = in_ch

    if fetch_props:
        print(' => Fetching followers...')
        key       = 'followers_of:{}'.format(user.id)
        followers = gen_to_list(user.followers(etag = etag(key)), key)

        print(' => Fetching following...')
        key       = 'following_of:{}'.format(user.id)
        following = gen_to_list(user.following(etag = etag(key)), key)

        print(' => Fetching repositories...')
        key          = 'repositories_of:{}'.format(user.id)
        repositories = gen_to_list(gh.repositories_by(user.login, etag = etag(key)), key)

        print(' => Fetching starred repositories...')
        key     = 'starred_by:{}'.format(user.id)
        starred = gen_to_list(gh.starred_by(user.login, etag = etag(key)), key)

        print(' => Fetching organizations...')
        key  = 'organizations_with:{}'.format(user.id)
        orgs = gen_to_list(gh.organizations_with(user.login, etag = etag(key)), key)

        print(' => Fetching gists...')
        key  = 'gists_by:{}'.format(user.id)
        gists = gen_to_list(gh.gists_by(user.login, etag = etag(key)), key)
    else:
        followers = following = repositories = starred = orgs = gists = []

    repositories_dicts = [repo_to_dict(r) for r in repositories]
    starred_dicts      = [repo_to_dict(r) for r in starred]
    orgs_dicts         = [org_to_dict(o)  for o in orgs]
    gists_dicts        = [gist_to_dict(g) for g in gists]

    user_dict = user_to_dict(
        user=user,
        in_ch=in_ch,
        repositories=repositories_dicts,
        starred=starred_dicts,
        orgs=orgs_dicts,
        gists=gists_dicts,
        override=False
    )

    return objdict(
        user         = user_dict,
        repositories = repositories_dicts,
        starred      = starred_dicts,
        orgs         = orgs_dicts,
        gists        = gists_dicts,
        followers    = followers,
        following    = following
    )

def insert_user(user, in_ch=False):
    if in_ch:
        print(' => Refreshing...')
        user = user.refresh()

    res = fetch_user(user, in_ch)

    db.users.update_one({ '_id': user.id }, { '$set': res.user }, upsert=True)

    for repo in res.repositories:
        db.repositories.update_one({ '_id': repo._id }, { '$set': repo }, upsert=True)

    for repo in res.starred:
        db.repositories.update_one({ '_id': repo._id }, { '$set': repo }, upsert=True)

    for org in res.orgs:
        db.organizations.update_one({ '_id': org._id }, { '$set': org }, upsert=True)

    for gist in res.gists:
        db.gists.update_one({ '_id': gist._id }, { '$set': gist }, upsert=True)

    if in_ch:
        print(' => Inserting followers & following...')
        for f in res.followers:
            insert_user(f, in_ch=False)

        for f in res.following:
            insert_user(f, in_ch=False)

def show_rate_limit():
    rate       = gh.rate_limit()
    rate       = rate['resources']['core']
    limit      = rate['limit']
    remaining  = rate['remaining']
    reset      = rate['reset']
    reset_in_s = reset - int(time.time())
    reset_in   = str(datetime.timedelta(seconds = reset_in_s))

    print('GitHub API calls: {} remaining, reset to {} in {}\n'.format(remaining, limit, reset_in))

def get_token():
    GITHUB3_TOKEN = 'GITHUB3_TOKEN'
    token = os.environ.get(GITHUB3_TOKEN)

    if not token:
        print('Missing ' + GITHUB3_TOKEN + ' environment variable. Please check README.md.')
        sys.exit(1)

    return token

def github_login():
    print('Logging-in with GitHub...')
    return github3.login(token=get_token())

def get_mongo_conn_info():
    MONGO_HOST, MONGO_PORT = 'MONGO_HOST', 'MONGO_PORT'

    host = str(os.environ.get(MONGO_HOST)) or 'localhost'
    port = int(os.environ.get(MONGO_PORT)) or 27017

    return host, port

def get_mongo_db():
    mongoHost, mongoPort = get_mongo_conn_info()

    print('Connecting to MongoDB at {}:{}...'.format(mongoHost, mongoPort))

    client = MongoClient(mongoHost, mongoPort)

    db = client.ada

    try:
        db.current_op()
    except:
        print('Could not connect to MongoDB at {}:{}'.format(mongoHost, mongoPort))

        sys.exit(1)

    return db

if __name__ == '__main__':

    db = get_mongo_db()
    gh = github_login()
    show_rate_limit()

    en_users = search_users(location('Switzerland'))
    fr_users = search_users(location('Suisse'))
    de_users = search_users(location('Schweiz'))
    it_users = search_users(location('Svizzera'))
    ch_users = search_users(location('CH'))

    search_res = itertools.chain(en_users, fr_users, de_users, it_users, ch_users)

    for res in search_res:
        print('Processing user {}...'.format(res.user.login))
        insert_user(res.user, in_ch=True)

