
import os
import sys
import time
import datetime
import itertools

import github3

from pymongo import MongoClient

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

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

def gen_to_list(db, gen, key, *args):
    values = list(gen)
    key    = key.format(*args)

    # Disable useless E-Tag
    # etag = dict(key = key, etag = gen.etag)
    etag = None

    db.etags.replace_one({ 'key': key }, etag, upsert=True)

    return values

def etag(db, key, *args):
    # Disable useless E-Tag
    return None

    doc = db.etags.find_one({ 'key': key.format(*args) })

    if doc is None:
        return None

    return doc['etag']

def insert_user(db, user, in_ch=True, update=True):
    if db.users.find_one({ '_id': user.id }) and not update:
        print('Skipping existing user {}'.format(user.login))
        return

    print('Inserting user {}...'.format(user.login))

    user_dict = user_to_dict(user=user, in_ch=in_ch, override=in_ch)

    db.users.update_one({ '_id': user.id }, { '$set': user_dict }, upsert=True)

def user_to_dict(user, in_ch, followers=[], following=[], repositories=[], starred=[], orgs=[], gists=[], last_refresh=None, override=False):

    user_dict = objdict(
        _id   = user.id,
        login = user.login
    )

    if in_ch:
        user_dict['in_ch'] = True

    if override or user.name and len(user.name) > 0:
        user_dict['name'] = user.name

    if override or user.location and len(user.location) > 0:
        user_dict['location'] = user.location

    if override or user.company and len(user.company) > 0:
        user_dict['company'] = user.company

    if override or len(followers) > 0:
        user_dict['followers'] = [f.id for f in followers]

    if override or len(following) > 0:
        user_dict['following'] = [f.id for f in following]

    if override or len(repositories) > 0:
        user_dict['repositories'] = [r._id for r in repositories]

    if override or len(starred) > 0:
        user_dict['starred'] = [r._id for r in starred]

    if override or len(orgs) > 0:
        user_dict['organizations'] = [o._id for o in orgs]

    if override or len(gists) > 0:
        user_dict['gists'] = [g._id for g in gists]

    if last_refresh:
        user_dict['last_refresh'] = last_refresh

    return user_dict

def repo_to_dict(repo, refresh=False):
    if refresh:
        repo = repo.refresh()

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

def org_to_dict(org, refresh=False):
    if refresh:
        org = org.refresh()

    return objdict(
        _id         = org.id,
        login       = org.login,
        name        = org.name,
        description = org.description,
        blog        = org.blog
    )

def gist_to_dict(gist, refresh=False):
    if refresh:
        gist = gist.refresh()

    return objdict(
        _id            = gist.id,
        description    = gist.description,
        owner_id       = gist.owner.id,
        comments_count = gist.comments_count
    )

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

def is_rate_exceeded(rate, resource='core'):
    return rate['resources'][resource]['remaining'] <= 0

def wait_until(future_time):
    left = future_time - int(time.time())

    while left >= 0:
        print('{} seconds left'.format(left), end='\r')
        left = future_time - int(time.time())
        time.sleep(1)

    print('')

def show_rate_limit(gh, resources=['core'], oneline=False):
    rate = gh.rate_limit()

    def show_resource(resource, oneline=False):
        res        = rate['resources'][resource]
        limit      = res['limit']
        remaining  = res['remaining']
        reset      = res['reset']
        reset_in_s = reset - int(time.time())
        reset_in   = str(datetime.timedelta(seconds = reset_in_s))

        end = '\r' if oneline else '\n'

        print('GitHub API calls for \'{}\': {} remaining, reset to {} in {}'.format(resource, remaining, limit, reset_in), end = end)

    if len(resources) == 1 and oneline:
        show_resource(resources[0], oneline)
        return

    for resource in resources:
        show_resource(resource)

    print('')

def get_mongo_conn_info():
    MONGO_HOST, MONGO_PORT = 'MONGO_HOST', 'MONGO_PORT'

    host = os.environ.get(MONGO_HOST) or 'localhost'
    port = os.environ.get(MONGO_PORT) or 27017

    return str(host), int(port)

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

