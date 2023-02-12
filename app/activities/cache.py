import logging
from ast import literal_eval

import filesystem_database as fs_db

from ..util.read_config import get_database_names

logger = logging.getLogger()
activitySummitsFilename = get_database_names()['activitySummitsFilename']
activityNode = fs_db.dbNode(activitySummitsFilename)
   
def get_cached_activity_summits(id: str) -> list:
    return bytes_to_names(activityNode.get(id))

def save_activity_summits_to_cache(id: str, summits: list) -> None:
    key = dict(activityNode.keyNames.items()).get(id)
    if not key:
        key = 1
        while key in activityNode.keys:
            key += 1
        activityNode.mkKey(key, id)
    activityNode.set(id, names_to_bytes(summits))

def get_cached_activity_ids() -> list:
    return list(activityNode.keyNames.keys())

def names_to_bytes(names):
    return bytes(str(names), 'utf-8')

def bytes_to_names(b):
    return literal_eval(b.decode("utf-8"))
    
