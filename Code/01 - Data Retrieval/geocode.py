
import geocoder

import os
import sys
import time
import datetime

import itertools
import github3

from pymongo import ASCENDING

from utils import *

def geocode_location(location):
    if location is not None and len(location) > 2:
        geo = geocoder.google(location)

        if geo.ok:
            return geo

    return None

def geocode_user(user):
    loc = geocode_location(user.location)

    if loc is not None:
        print(' => Found location: {}, {}, {} ({}, {})\n'.format(loc.city, loc.state, loc.country, loc.lat, loc.lng))

        loc_dict = dict(
            lat=loc.lat,
            lng=loc.lng,
            city=loc.city,
            state=loc.state,
            country=loc.country
        )

        db.users.update_one({ '_id': user._id }, { '$set': { 'geocode': loc_dict }}, upsert=True)
    else:
        print(' => No location found\n')

if __name__ == '__main__':

    db = get_mongo_db()

    ch_users = db.users.find({
        'in_ch': True,
        'location': { '$ne': None },
        'geocode': None
    }).sort('username', ASCENDING)

    i = 1
    total = ch_users.count()

    for user in ch_users:
        count = '{}/{}'.format(i, total)
        print('{} - Geocoding user \'{}\' with location \'{}\''.format(count, user['login'], user['location']))

        geocode_user(kobjdict(user))

        i += 1

