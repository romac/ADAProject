
import os
import sys
import time
import datetime

import itertools
import github3

from pymongo import ASCENDING, DESCENDING

from utils import *


if __name__ == '__main__':

    db = get_mongo_db()

    geo_users = db.users.find({
        'geocode': { '$ne': None }
    }).sort('username', ASCENDING)

    count = geo_users.count()

    print('Creating GeoJSON field...')

    i = 1

    for user in geo_users:
        lat = user['geocode']['lat']
        lng = user['geocode']['lng']

        geojson = {
            'type': 'Point',
            'coordinates': [ lng, lat ]
        }

        print('{}/{}      '.format(i, count), end = '\r')

        db.users.update_one(
            { '_id': user['_id'] },
            { '$set': { 'geocode.2dsphere': geojson } }
        )

        i += 1

