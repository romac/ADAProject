
import geocoder

import os
import sys
import time
import datetime

import itertools
import github3

from pymongo import ASCENDING, DESCENDING

from utils import *

location_strict_map = {
    'ch': 'Switzerland'
}

lausanne = 'Lausanne, Switzerland'
zurich   = 'Zürich, Switzerland'
geneva   = 'Geneva, Switzerland'
bern     = 'Bern, Switzerland'
basel    = 'Basel, Switzerland'

location_sub_map = [
    ('epfl'       , lausanne),
    ('ethz'       , zurich),
    ('zurich'     , zurich),
    ('zürich'     , zurich),
    ('bern'       , bern),
    ('lausanne'   , lausanne),
    ('basel'      , basel),
    ('cern'       , geneva),
    ('genf'       , geneva),
    ('geneva'     , geneva),
    ('geneve'     , geneva),
    ('genève'     , geneva),
    ('wetzikon'   , zurich),
    ('rapperswil' , zurich),
    ('thurgau'    , 'Thurgau, Switzerland'),
    ('yverdoom'   , 'Yverdon, Switzerland'),
    ('neuchatel'  , 'Neuchâtel, Switzerland'),
    ('neuchâtel'  , 'Neuchâtel, Switzerland'),
    ('martigny'   , 'Martigny, Switzerland'),
    ('switzerland' , 'Switzerland'),
    ('suisse' , 'Switzerland'),
    ('schweiz' , 'Switzerland'),
    ('svizzera' , 'Switzerland'),
]

def improve_location(location):
    location = location.strip()
    lower    = location.lower()

    if lower in location_strict_map:
        new_loc = location_strict_map[lower]
        print(' => Replacing \'{}\' with \'{}\''.format(location, new_loc))
        return new_loc

    for needle, replacement in location_sub_map:
        if needle in lower:
            print(' => Replacing \'{}\' with \'{}\''.format(location, replacement))
            return replacement

    return location


def geocode_location(location):
    if location is not None and len(location) > 1:
        old = location
        location = improve_location(location)

        geo = geocoder.google(location)

        if geo.ok:
            return geo

        # print(' => No location found using Google, retrying with OpenStreetMap...')

        # time.sleep(1)
        # geo = geocoder.osm(location)

        # if geo.ok:
        #     return geo

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
        'geocode': { '$eq': None }
    }).sort('username', DESCENDING)

    i = 1
    total = ch_users.count()

    for user in ch_users:
        count = '{}/{}'.format(i, total)
        print('{} - Geocoding user \'{}\' with location \'{}\''.format(count, user['login'], user['location']))

        geocode_user(kobjdict(user))

        i += 1

