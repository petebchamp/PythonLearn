#Reference: https://www.dataquest.io/blog/apartment-finding-slackbot/

from craigslist import CraigslistHousing
import mpu

KM_TO_MILE = 0.621371
MAX_DIST = 1.0
APT_COUNT = 100
SEARCH_DISTANCE = 4
ZIP_CODE = '94720'
MAX_PRICE = 2800
MIN_PRICE = 1800

BART = {
    #"northberkelybart": [37.8739642,-122.2834432],
    "downtownberkelybart": [37.8701043,-122.2681332],
    "ashbybart": [37.8530641,-122.2699463],
    "rockridgebart": [37.844713,-122.2513774]#,
    #"macarthurbart": [37.8290651,-122.2670469]
}

POOL = {
    "calaquaticmasters": [37.8650469,-122.2471422]#,
    #"berkeleyaquaticmasters": [37.8825067,-122.2788882],
    #"manateeaquaticmasters": [37.8352848,-122.2832072]
}

cl = CraigslistHousing(site='sfbay', area='eby', category='apa', filters={'search_distance': SEARCH_DISTANCE, 'zip_code': ZIP_CODE, 'max_price': MAX_PRICE, 'min_price': MIN_PRICE})
apts = cl.get_results(sort_by='newest', geotagged=True, limit=APT_COUNT)
for apt in apts:
    if 'STUDIO' in apt['name'] or 'CARPET' in apt['name']:
        continue
    
    near_bart = False
    near_pool = False
    
    for bart, coords in BART.items():
        bart_dist = mpu.haversine_distance((coords[0], coords[1]), (apt['geotag'][0], apt['geotag'][1]))
        bart_dist = bart_dist * KM_TO_MILE
        if bart_dist <= MAX_DIST:
            near_bart = True
            break
        
    for pool, coords in POOL.items():
        pool_dist = mpu.haversine_distance((coords[0], coords[1]), (apt['geotag'][0], apt['geotag'][1]))
        pool_dist = pool_dist * KM_TO_MILE
        if pool_dist <= MAX_DIST:
            near_pool = True
            break
        
    if near_bart and near_pool:
        print(bart, ': ', round(bart_dist, 1))
        print(pool, ': ', round(pool_dist, 1))
        print(apt['name'])
        print(apt['price'])
        print(apt['url'])
        print()