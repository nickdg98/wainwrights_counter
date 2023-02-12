import requests
from ..activities.activities import TooManyRequests

def get_current_user(auth_header: str) -> dict:
    res = requests.get(
        "https://www.strava.com/api/v3/athlete/",
        headers={'Authorization': auth_header}
    )
    if res.status_code == 429:
        raise TooManyRequests
    else:
        return res.json()
