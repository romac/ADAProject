
import geocoder

import os
import sys
import time
import datetime

import itertools
import github3

from pymongo import MongoClient

from utils import *
from fetch import insert_user

def geocode_location(location):
    if location is not None and len(location) > 2:
        geo = geocoder.google(location)

        if geo.ok:
            return geo

    return None

def geocode_user(user):
    print('Geocoding user \'{}\' with location \'{}\''.format(user.login, user.location))

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

    ch_users = db.users.find({ 'in_ch': True, 'geocode.lat': None })

    for user in ch_users:
        geocode_user(kobjdict(user))

