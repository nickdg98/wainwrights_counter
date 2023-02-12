import configparser
import logging
from datetime import timedelta

from flask import Flask, render_template, request

from app.user.cache import get_cached_user_ids, get_user_activities, get_user_last_updated, save_user_to_cache

from .activities.activities import get_activity_ids, get_summits_from_strava
from .activities.cache import (get_cached_activity_ids,
                               get_cached_activity_summits,
                               save_activity_summits_to_cache)
from .summits import wainwrights
from .user.athlete import get_current_user
from .util.errors import TooManyRequests

logging.basicConfig(level=logging.INFO)
config = configparser.ConfigParser()
config.read('config.ini')

app = Flask(__name__)

@app.route("/")
def home():
    code = request.args.get('code')
    if code:
        return render_template('auto_commuter.html', code=code, redirect_uri=config['strava']['redirect_uri'], client_id=config['strava']['client_id'], client_secret=config['strava']['client_secret'])
    return render_template('home.html', redirect_uri=config['strava']['redirect_uri'], client_id=config['strava']['client_id'])

@app.route("/wainwrights")
def list_hills():
    # returns dict of hill name, (lat,long) for each of the wainwrights
    return {k.name: (k.lat, k.long) for k in wainwrights}

@app.route("/get_bagged")
def get_bagged():
    auth_header = request.headers['Authorization']
    try:
        athlete = get_current_user(auth_header)
        athlete['id'] = str(athlete['id'])
    except TooManyRequests:
        athlete = dict()
    app.logger.info(f"{athlete.get('firstname')} {athlete.get('lastname')} requested bagged activities")
    date_last_checked = get_user_last_updated(athlete['id'])
    activity_ids_before_then = get_user_activities(athlete['id'])
    if athlete['id'] in get_cached_user_ids():
        app.logger.info(f"Has previously requested this at {date_last_checked + timedelta(days=7)} and that process found {len(activity_ids_before_then)} activities")
    else:
        app.logger.info("this is first time user has requested")

    cached_ids = set(get_cached_activity_ids())   
    try:
        activity_ids_since_then = set(get_activity_ids(auth_header, date_from=date_last_checked))
    except TooManyRequests:
        return {'bagged': []}
    ids = set(activity_ids_before_then).union(activity_ids_since_then) if activity_ids_before_then else activity_ids_since_then
    save_user_to_cache(athlete['id'], ids)
    get_from_cache_ids = ids.intersection(cached_ids)
    get_from_strava_ids = ids - get_from_cache_ids
    app.logger.info(f"user has {len(ids)} activities")
    app.logger.info(f"already scanned {len(cached_ids)} of them")
    bagged = []
    if len(get_from_cache_ids): app.logger.info("doing cached ids")
    for id in get_from_cache_ids:
        bagged.extend(get_cached_activity_summits(id))
    if len(get_from_strava_ids): app.logger.info("doing new ids")
    for ix, id in enumerate(get_from_strava_ids):
        try:
            bagged.extend(get_summits_from_strava(id, auth_header))
        except TooManyRequests:
            break
        app.logger.info(f"done {ix+1} of {len(get_from_strava_ids)} strava calls")
    app.logger.info(f"returning bagged peaks as {list(set(bagged))}")
    return {'bagged': list(set(bagged))}

@app.route("/get_athlete")
def get_athlete():
    auth_header = request.headers['Authorization']
    try:
        athlete = get_current_user(auth_header)
    except TooManyRequests:
        athlete = dict()
    return {"athlete": {
        "id": athlete.get('id'),
        "name": f"{athlete.get('firstname')} {athlete.get('lastname')}"
    }}
