import logging

import requests
from geopy.distance import geodesic as GD

from ..summits import get_summits_on_polyline
from ..util.errors import TooManyRequests
from ..util.read_config import get_centre_coords, get_max_pages, get_per_page
from .cache import (get_cached_activity_ids, get_cached_activity_summits,
                    save_activity_summits_to_cache)

logger = logging.getLogger()

allowed_sports = ["Hike", "RockClimbing", "Run", "Snowshoe", "TrailRun", "Walk"]
        
def get_summits_from_strava(id: str, auth_header: str) -> list:        
    res = requests.get(
        "https://www.strava.com/api/v3/activities/" + str(id),
        headers={'Authorization': auth_header}
    )
    if res.status_code == 429:
        raise TooManyRequests
    else:
        activity = res.json()
    if activity.get('map') and activity['map'].get('polyline'):
        polyline = activity['map']['polyline']
        summits = get_summits_on_polyline(polyline)
    else:
        summits = []
    save_activity_summits_to_cache(id, summits)
    return summits
           
def get_url(page, date_from = None):
    url = f"https://www.strava.com/api/v3/athlete/activities?per_page={get_per_page()}&page={page}"
    if date_from:
        url += f"&after={int(date_from.timestamp())}"
        logger.info(f"filtering using url {url}")
    return url

def get_activity_ids(auth_header: str, date_from = None) -> list:
    ids = []
    page = 1
    keep_going = True
    while keep_going:
        res = requests.get(
            get_url(page, date_from),
            headers={'Authorization': auth_header}
        )
        if res.status_code == 429:
            raise TooManyRequests
        else:
            activities = res.json()
        batch = []
        if isinstance(activities, list):
            batch = activities
        if isinstance(activities, dict) and 'id' in activities:
            batch = [activities]
        logger.info(f"{page}, {get_per_page()}, {len(batch)}")
        ids.extend([str(a['id']) for a in batch if a['sport_type'] in allowed_sports and GD(a['start_latlng'],get_centre_coords()).km < 100])
        page += 1
        if len(batch) < get_per_page() or page > get_max_pages():
            keep_going = False
    return ids
    