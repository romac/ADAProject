
import json

from github3.exceptions import ForbiddenError

from utils import *

def insert_username(username, num=0, force_check_rate=False):
    if num % 100 == 0 or force_check_rate:
        rate = gh.rate_limit()
        if is_rate_exceeded(rate):
            print('Rate limit exceeded!')
            wait_until(rate['resources']['core']['reset'])

    print('Fetching user {}...'.format(username))

    try:
        user = gh.user(username)
    except ForbiddenError:
        return insert_username(username, num, force_check_rate=True)

    if not user or not user.id:
        print(' => User doesn\'t exists')
        return

    print(' => Got user #{}'.format(user.id))

    user_dict = user_to_dict(user, in_ch=True)

    db.users.update_one({ '_id': user.id }, { '$set': user_dict }, upsert=True)

if __name__ == '__main__':

    db = get_mongo_db()
    gh = github_login()

    show_rate_limit(gh)

    users_file = 'git_awards_ch_users.json'
    usernames  = json.load(open(users_file, 'r'))

    for username, i in zip(usernames, range(len(usernames))):
        insert_username(username, i)

