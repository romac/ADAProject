
import os
import sys
import time
import datetime

import itertools
import github3

from pymongo import MongoClient

from github3.exceptions import ForbiddenError

from utils import *

def fetch_user_infos(user, in_ch=False, force=True):
    print(' => Fetching followers...')
    key       = 'followers_of:{}'.format(user.id)
    followers = gen_to_list(db, user.followers(etag = etag(db, key) if not force else None), key)
    print('     => Found {}'.format(len(followers)))

    print(' => Fetching following...')
    key       = 'following_of:{}'.format(user.id)
    following = gen_to_list(db, user.following(etag = etag(db, key) if not force else None), key)
    print('     => Found {}'.format(len(following)))

    print(' => Fetching repositories...')
    key          = 'repositories_of:{}'.format(user.id)
    repositories = gen_to_list(db, gh.repositories_by(user.login, etag = etag(db, key) if not force else None), key)
    print('     => Found {}'.format(len(repositories)))

    print(' => Fetching starred repositories...')
    key     = 'starred_by:{}'.format(user.id)
    starred = gen_to_list(db, gh.starred_by(user.login, etag = etag(db, key) if not force else None), key)
    print('     => Found {}'.format(len(starred)))

    print(' => Fetching organizations...')
    key  = 'organizations_with:{}'.format(user.id)
    orgs = gen_to_list(db, gh.organizations_with(user.login, etag = etag(db, key) if not force else None), key)
    print('     => Found {}'.format(len(orgs)))

    print(' => Fetching gists...')
    key  = 'gists_by:{}'.format(user.id)
    gists = gen_to_list(db, gh.gists_by(user.login, etag = etag(db, key) if not force else None), key)
    print('     => Found {}'.format(len(gists)))

    repositories_dicts = [repo_to_dict(r) for r in repositories]
    starred_dicts      = [repo_to_dict(r) for r in starred]
    orgs_dicts         = [org_to_dict(o)  for o in orgs]
    gists_dicts        = [gist_to_dict(g) for g in gists]

    user_dict = user_to_dict(
        user=user,
        in_ch=in_ch,
        followers=followers,
        following=following,
        repositories=repositories_dicts,
        starred=starred_dicts,
        orgs=orgs_dicts,
        gists=gists_dicts,
        last_refresh=datetime.datetime.utcnow(),
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

def refresh_user(user, num=0, in_ch=False, force_check_rate=False):
    if num % 100 == 0 or force_check_rate:
        rate = gh.rate_limit()
        if is_rate_exceeded(rate):
            print('Rate limit exceeded!')
            wait_until(rate['resources']['core']['reset'])

    print('Refreshing user {}...'.format(user.login))

    try:
        gh_user = gh.user(user.login)
        res     = fetch_user_infos(gh_user, in_ch)
    except ForbiddenError:
        return refresh_user(user, num, in_ch, True)

    db.users.update_one({ '_id': user._id }, { '$set': res.user }, upsert=True)

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
            insert_user(db, user=f, in_ch=False, update=False)

        for f in res.following:
            insert_user(db, user=f, in_ch=False, update=False)

if __name__ == '__main__':

    db = get_mongo_db()
    gh = github_login()

    show_rate_limit(gh)

    ch_users = list(db.users.find({
        'in_ch': True,
        'last_refresh': None
    }))

    for user, i in zip(ch_users, range(len(ch_users))):
        refresh_user(kobjdict(user), i, in_ch=True)

