import logging
logger = logging.getLogger()

class TooManyRequests(Exception):
    def __init__(self, message="Strava gave a 429 response"):
        logger.warn(message)
        self.message = message
        super().__init__(self.message)