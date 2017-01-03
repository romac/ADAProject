
import os
import sys
import time
import datetime

import itertools
import github3

from pymongo import MongoClient

class kobjdict(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)

def objdict(**kwargs):
    return kobjdict(dict(**kwargs))

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
    return objdict(
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

def org_to_dict(org):
    org = org.refresh()

    return objdict(
        _id         = org.id,
        login       = org.login,
        name        = org.name,
        description = org.description,
        blog        = org.blog
    )

def gist_to_dict(gist):
    gist = gist.refresh()

    return objdict(
        _id            = gist.id,
        description    = gist.description,
        owner_id       = gist.owner.id,
        comments_count = gist.comments_count
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

    user_dict = objdict(
        _id          = user.id,
        login        = user.login,
        name         = user.name,
        location     = user.location,
        company      = user.company
    )

    if len(followers) > 0:
        user_dict['followers']     = [f.id for f in followers]

    if len(following) > 0:
        user_dict['following']     = [f.id for f in following]

    if len(repositories) > 0:
        user_dict['repositories']  = [r._id for r in repositories_dicts]

    if len(starred) > 0:
        user_dict['starred']       = [r._id for r in starred_dicts]

    if len(orgs) > 0:
        user_dict['organizations'] = [o._id for o in orgs_dicts]

    if len(gists) > 0:
        user_dict['gists']         = [g._id for g in gists_dicts]

    return objdict(
        user         = user_dict,
        repositories = repositories_dicts,
        starred      = starred_dicts,
        orgs         = orgs_dicts,
        gists        = gists_dicts,
        followers    = followers,
        following    = following
    )

def insert_user(user, insert_follow=False):
    if insert_follow:
        print('Refreshing user {}...'.format(user.login))
        user = user.refresh()

    res = user_to_dict(user, insert_follow)

    db.users.update_one({ '_id': user.id }, { '$set': res.user }, upsert=True)

    for repo in res.repositories:
        db.repositories.update_one({ '_id': repo._id }, { '$set': repo }, upsert=True)

    for repo in res.starred:
        db.repositories.update_one({ '_id': repo._id }, { '$set': repo }, upsert=True)

    for org in res.orgs:
        db.organizations.update_one({ '_id': org._id }, { '$set': org }, upsert=True)

    for gist in res.gists:
        db.gists.update_one({ '_id': gist._id }, { '$set': gist }, upsert=True)

    if insert_follow:
        print(' => Inserting followers & following...')
        for f in res.followers:
            insert_user(f, False)

        for f in res.following:
            insert_user(f, False)

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

def login():
    return github3.login(token=get_token())

if __name__ == '__main__':
    client = MongoClient('localhost', 27017)
    db = client.ada

    gh = login()

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

