from env import config
# FROM PANDAPY APP
SPOTIFY_CLIENT_SECRET = config("SPOTIFY_CLIENT_SECRET", default = None)
SPOTIFY_CLIENT_ID = config("SPOTIFY_CLIENT_ID", default = None)
SPOTIFY_USER_ID = config("SPOTIFY_USER_ID", default = None)
SPOTIFY_REDIRECT_URL = config("SPOTIFY_REDIRECT_URL", default = None)
