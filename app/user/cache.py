import logging
from ast import literal_eval
from datetime import datetime, timedelta

import filesystem_database as fs_db

from ..util.read_config import get_database_names

logger = logging.getLogger()

userSummitsFilename = get_database_names()['userSummitsFilename']
userNode = fs_db.dbNode(userSummitsFilename)
if 0 not in userNode.nodes:
    userNode.mkNode(0, 'checked_until')
dateNode = userNode.node(0)
if 1 not in userNode.nodes:
    userNode.mkNode(1, 'activity_ids')
activitiesNode = userNode.node(1)

def get_user_activities(id: str) -> list:
    if id in get_cached_user_ids():
        return bytes_to_strings(activitiesNode.get(id))

def get_user_last_updated(id: str) -> datetime:
    if id in get_cached_user_ids():
        return bytes_to_datetime(dateNode.get(id))

def save_user_to_cache(id: str, activities: list) -> None:
    logger.info(f"saving user {id} to db")
    key = dict(dateNode.keyNames.items()).get(id)
    if not key:
        key = 1
        while key in dateNode.keys:
            key += 1
        dateNode.mkKey(key, id)
    
    key = dict(activitiesNode.keyNames.items()).get(id)
    if not key:
        key = 1
        while key in activitiesNode.keys:
            key += 1
        activitiesNode.mkKey(key, id)
    
    activitiesNode.set(id, strings_to_bytes(activities))
    dateNode.set(id, datetime_to_bytes(datetime.now() - timedelta(days=7)))

def get_cached_user_ids() -> list:
    return list(dateNode.keyNames.keys())

def strings_to_bytes(s):
    return bytes(str(s), 'utf-8')

def bytes_to_strings(b):
    return literal_eval(b.decode("utf-8"))

format = "%m/%d/%Y %H:%M:%S"
def datetime_to_bytes(d):
    return bytes(d.strftime(format), 'utf-8')

def bytes_to_datetime(b):
    return datetime.strptime(b.decode("utf-8"), format)

    
