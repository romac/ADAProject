
# Connecting to DB
from utils import get_mongo_db

import pickle

import numpy as np
import pandas as pd
from scipy import stats

SETTINGS = {
    't_test' : True
}

db = get_mongo_db()

def log(stash, text):
    stash.append(text)

def get_user(username):
    return db.users.find_one({ 'login' : username })

def collect_stats(username):
    stash = []
    usr = get_user(username)
    rest_of_users_stats = {}

    def get_users():
        # Get users from DB
        res = db.users.find({ 'in_ch': True, 'repositories': { '$ne': None } })

        users = []

        # For each user, find his repositories
        for user in res:
            repos = db.repositories.find(
                { '_id': { '$in': user['repositories'] } }
            )

            stars = 0
            for repo in repos:
                stars = stars + repo['stargazers_count']

            starred       = user.get('starred', [])
            following     = user.get('following', [])
            followers     = user.get('followers', [])
            organizations = user.get('organizations', [])
            gists         = user.get('gists', [])
            repositories  = user.get('repositories', [])

            users.append({
                '_id': user['_id'],
                'login': user['login'],
                'name': user['name'],
                'location': user['location'],
                'repositories_docs': list(repos),
                'followers' : len(followers),
                'starred' : len(starred),
                'following' : len(following),
                'orgs' : len(organizations),
                'gists' : len(gists),
                'repos' : len(repositories),
                'stars' : stars
            })

        log(stash, "Our dataset includes {} users.".format(len(users)))

        all_users = pd.DataFrame(users)

        current_user = all_users.loc[all_users['_id'] == usr['_id']]
        rest_of_users = all_users[all_users['_id'] != usr['_id']]

        return (current_user, rest_of_users)

    (current_user, rest_of_users) = get_users()

    def mean_starred():
        mean_starred = int(rest_of_users['starred'].mean())
        std_starred = rest_of_users['starred'].std()
        rest_of_users_stats['starred'] = mean_starred

        log(stash, "On average, swiss users of Github have starred {} repositories.".format(mean_starred))

        log(stash, "You have starred {} repositories.".format(int(current_user['starred'])))

        if int(current_user['starred']) > rest_of_users['starred'].mean():
            log(stash, "You have starred more repositories than the average !")
        else:
            log(stash, "You have starred less repositories than the average")

        log(stash, " => DELTA = {}".format(int(current_user['starred']) - mean_starred))

        if SETTINGS['t_test'] is True:
            (t_statistic, p_value) = stats.ttest_1samp(rest_of_users['starred'], np.mean(current_user['starred']))
            if abs(t_statistic) > 6.31:
                log(stash, "The results is statistically significant ! (95% confidence level)")
            else:
                log(stash, "The result is not provable to be statistically significant, with a t-value = {} and p-value = {}".format(t_statistic, p_value))

    def orgs_num():
        mean_orgs = rest_of_users['orgs'].mean()
        std_orgs = rest_of_users['orgs'].std()
        rest_of_users_stats['orgs'] = mean_orgs

        log(stash, "On average, swiss users of Github are part of {} organizations (± {}).".format(mean_orgs, std_orgs))

        log(stash, "You are part of {} organization(s).".format(int(current_user['orgs'])))

        if int(current_user['orgs']) > mean_orgs:
            log(stash, "You are part of more organizations than the average !")
        else:
            log(stash, "You are part of less organizations than the average")

        log(stash, " => DELTA = {}".format(int(current_user['orgs']) - mean_orgs))

        if SETTINGS['t_test'] is True:
            (t_statistic, p_value) = stats.ttest_1samp(rest_of_users['orgs'], np.mean(current_user['orgs']))
            if abs(t_statistic) > 6.31:
                log(stash, "The results is statistically significant ! (95% confidence level)")
            else:
                log(stash, "The result is not provable to be statistically significant, with a t-value = {} and p-value = {}".format(t_statistic, p_value))

    def repos_num():
        mean_repos = rest_of_users['repos'].mean()
        std_repos = rest_of_users['repos'].std()
        rest_of_users_stats['repos'] = mean_repos

        log(stash, "On average, swiss users of Github have created {} repositories (± {}).".format(mean_repos, std_repos))

        log(stash, "You have created {} repositories.".format(int(current_user['repos'])))

        if int(current_user['repos']) > mean_repos:
            log(stash, "You have created more repositories than the average !")
        else:
            log(stash, "You have created less repositories than the average")

        log(stash, " => DELTA = {}".format(int(current_user['repos']) - mean_repos))

        if SETTINGS['t_test'] is True:
            (t_statistic, p_value) = stats.ttest_1samp(rest_of_users['repos'], np.mean(current_user['repos']))
            if abs(t_statistic) > 6.31:
                log(stash, "The result is statistically significant ! (95% confidence level)")
            else:
                log(stash, "The result is not provable to be statistically significant at 95% confidence, with a t-value = {} and p-value = {}".format(t_statistic, p_value))

    def followers_num():
        mean_followers = rest_of_users['followers'].mean()
        std_followers = rest_of_users['followers'].std()
        rest_of_users_stats['followers'] = mean_followers

        log(stash, "On average, swiss users of Github have {} followers (± {}).".format(mean_followers, std_followers))

        log(stash, "You have got {} followers.".format(int(current_user['followers'])))

        if int(current_user['followers']) > mean_followers:
            log(stash, "You have more followers than the average !")
        else:
            log(stash, "You have less followers than the average.")

        log(stash, " => DELTA = {}".format(int(current_user['followers']) - mean_followers))

        if SETTINGS['t_test'] is True:
            (t_statistic, p_value) = stats.ttest_1samp(rest_of_users['followers'], np.mean(current_user['followers']))
            if abs(t_statistic) > 6.31:
                log(stash, "The result is statistically significant ! (95% confidence level)")
            else:
                log(stash, "The result is not provable to be statistically significant at 95% confidence, with a t-value = {} and p-value = {}".format(t_statistic, p_value))


    def stars_num():
        mean_stars = rest_of_users['stars'].mean()
        std_stars = rest_of_users['stars'].std()
        rest_of_users_stats['stars'] = mean_stars

        log(stash, "On average, swiss users of Github have {} accumulated stars (± {}).".format(mean_stars, std_stars))

        log(stash, "You have got {} accumulated stars.".format(int(current_user['stars'])))

        if int(current_user['stars']) > mean_stars:
            log(stash, "You have more stars than the average !")
        else:
            log(stash, "You have less stars than the average.")

        log(stash, " => DELTA = {}".format(int(current_user['stars']) - mean_stars))

        if SETTINGS['t_test'] is True:
            (t_statistic, p_value) = stats.ttest_1samp(rest_of_users['stars'], np.mean(current_user['stars']))
            if abs(t_statistic) > 6.31:
                log(stash, "The result is statistically significant ! (95% confidence level)")
            else:
                log(stash, "The result is not provable to be statistically significant at 95% confidence, with a t-value = {} and p-value = {}".format(t_statistic, p_value))

    user_stats = {
        'gists' : int(current_user['gists']),
        'orgs' : int(current_user['orgs']),
        'repos' : int(current_user['repos']),
        'starred' : int(current_user['starred']),
        'followers' : int(current_user['followers']),
        'stars' : int(current_user['stars'])
    }

    statistics = { 'rest' : rest_of_users_stats, 'user' : user_stats }

    mean_starred()
    orgs_num()
    repos_num()
    followers_num()
    stars_num()

    return (stash, statistics)

