
import os
import sys
import time
import datetime

import itertools
import github3

from pymongo import MongoClient

def location(loc):
    return 'location:{}'.format(loc)

def search_users(query):
    key  = 'search_users:{}'.format(query)
    gen  = gh.search_users(query, number=10, etag=etag(key))

    return gen_to_list(gen, key)

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

def repo_to_dict(repo):
    return dict(
        _id               = repo.id,
        name              = repo.name,
        owner_id          = repo.owner.id,
        language          = repo.language,
        forks_count       = repo.forks_count,
        open_issues       = repo.open_issues,
        watchers_count    = repo.watchers_count,
        full_name         = repo.full_name,
        created_at        = repo.created_at,
        fork              = repo.fork,
        has_downloads     = repo.has_downloads,
        homepage          = repo.homepage,
        stargazers_count  = repo.stargazers_count,
        open_issues_count = repo.open_issues_count,
        has_pages         = repo.has_pages,
        has_issues        = repo.has_issues,
        private           = repo.private,
        size              = repo.size,
        clone_url         = repo.clone_url
    )

def user_to_dict(user, fetch=False):
    if fetch:
        print(' => Fetching followers...')
        key       = 'followers_of:{}'.format(user.id)
        followers = gen_to_list(user.followers(etag = etag(key)), key)

        print(' => Fetching following...')
        key       = 'following_of:{}'.format(user.id)
        following = gen_to_list(user.following(etag = etag(key)), key)

        print(' => Fetching repositories...')
        key          = 'repositories_of:{}'.format(user.id)
        repositories = gen_to_list(gh.repositories_by(user.login, etag = etag(key)), key)
    else:
        followers = following = repositories = []

    followers_ids = [f.id for f in followers]
    following_ids = [f.id for f in following]

    repositories_dicts = [repo_to_dict(r) for r in repositories]

    user_dict = dict(
        _id          = user.id,
        login        = user.login,
        name         = user.name,
        location     = user.location,
        company      = user.company
    )

    if len(followers) > 0:
        user_dict['followers'] = followers_ids

    if len(following) > 0:
        user_dict['following'] = following_ids

    if len(repositories) > 0:
        user_dict['repositories'] = repositories_dicts

    return (user_dict, followers, following)

def insert_user(user, insert_follow=False):
    print('{}Refreshing user {}...'.format('' if insert_follow else ' * ', user.login))

    user = user.refresh()

    (user_dict, followers, following) = user_to_dict(user, insert_follow)

    print('{}Inserting user {}...'.format('' if insert_follow else ' * ', user.login))

    db.users.update_one({ '_id': user.id }, { '$set': user_dict }, upsert=True)

    # if insert_follow:
    #     for f in followers:
    #         insert_user(f, False)

    #     for f in following:
    #         insert_user(f, False)

def show_rate_limit():
    rate       = gh.rate_limit()
    rate       = rate['resources']['core']
    limit      = rate['limit']
    remaining  = rate['remaining']
    reset      = rate['reset']
    reset_in_s = reset - int(time.time())
    reset_in   = str(datetime.timedelta(seconds = reset_in_s))

    print('GitHub API calls: {} remaining, reset to {} in {}\n'.format(remaining, limit, reset_in))

if __name__ == '__main__':

    GITHUB3_TOKEN = 'GITHUB3_TOKEN'
    token = os.environ.get(GITHUB3_TOKEN)

    if not token:
        print('Missing ' + GITHUB3_TOKEN + ' environment variable. Please check README.md.')
        sys.exit(1)

    client = MongoClient('localhost', 27017)
    db = client.ada

    gh = github3.login(token=token)

    show_rate_limit()

    en_users = search_users(location('Switzerland'))
    fr_users = search_users(location('Suisse'))
    de_users = search_users(location('Schweiz'))
    it_users = search_users(location('Svizzera'))
    ch_users = search_users(location('CH'))

    search_res = itertools.chain(en_users, fr_users, de_users, it_users, ch_users)

    for res in search_res:
        print('Processing user {}...'.format(res.user.login))
        insert_user(res.user, True)

