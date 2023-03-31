import json
import requests
import uuid
from urllib.parse import urlencode
from requests_oauthlib import OAuth2Session # pip install requests-oauthlib
from requests.auth import HTTPBasicAuth
# Spotify package of python 
from spotify_secrets import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_USER_ID, SPOTIFY_REDIRECT_URL



from spotifypy import Spotify
"""
    Automate Spotify with Python
"""

class SpotifyPlayList(Spotify):
    SPOTIFY_URL = "https://api.spotify.com/v1/users/"
    SCOPE = ["user-read-email", "playlist-read-collaborative", "playlist-modify-public"]
    REDIRECT_URL = SPOTIFY_REDIRECT_URL
    SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
    SPOTIFY_AUTHORIZATION_URL = "https://accounts.spotify.com/authorize"


    def __init__(self, client_id, client_secret, user_id) -> None:
        super().__init__(client_id, client_secret)
        self.user_id = user_id

    
    def authorize_spotify_oAuth(self):
        """
        This authorization proccess so automatically sign in user if user already have signed up
        then return "Authorization": f"Bearer {your access token}"
        """
        state = uuid.uuid4()
        spotify = OAuth2Session(self.client_id, scope=self.SCOPE, redirect_uri=self.REDIRECT_URL)
        #REDIRECT USER TO SPOTIFY FOR AUTHORIZATION
        authorization_url, _ = spotify.authorization_url(self.SPOTIFY_AUTHORIZATION_URL, state=state)
        print(f"\t\tPlease go here and authorize\n{authorization_url}")
        redirect_response = input("Grab the full redirect URL here: ")

        auth = HTTPBasicAuth(self.client_id, self.client_secret)
        token = spotify.fetch_token(self.SPOTIFY_TOKEN_URL, auth=auth, authorization_response=redirect_response)
        access_token = token['access_token']
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        return headers

    
    # CREATE PLAYLIST
    def create_playlist(self, name, description, public = True):
        """
        This method create Playlist on your spotify' home automatically :)
        and return success json data.
        """
        headers = self.authorize_spotify_oAuth()
        self.__check_name_and_description(name)  # CHECK NAME
        self.__check_name_and_description(description) # CHECK DESCRIPTION
        self.exists_name_of_playlist(self, name) # CHECK NAME IF EXISTS IT DOESN'T CREATE PLAYLIST
        body = json.dumps({
            "name": name,
            "description": description,
            "public": public
        })
        full_path = f"{self.SPOTIFY_URL}{self.user_id}/playlists"
        r = requests.post(full_path, data=body, headers=headers)
        if r.status_code != 201:
            return r.json()
        return f"\t\t\tSUCCESSFULLY CREATED PLAYLIST.\n\n\n{r.json()}"



    # GET USER'S PLAYLISTS
    def get_user_playlists(self, limit = 10):
        """
        return json data of user's playlist :)
        """
        headers = self.get_headers()
        lookup_url = f"{self.SPOTIFY_URL}{self.user_id}/playlists"
        r = requests.get(lookup_url, headers=headers)
        if r.status_code != 200:
            return {}
        return r.json()


    
    # GET PLAYLIST
    def get_playlist(self):
        """
        Return single playlist object 
        """
        _id = self.get_id_of_playlist()
        base_url = "https://api.spotify.com/v1/playlists/"
        lookup_url = f"{base_url}{_id}"
        headers = self.get_headers()
        r = requests.get(lookup_url, headers=headers)
        if r.status_code != 200:
            return {}
        return r.json()

    
    # CHANGE PLAYLIST DETAILS
    def change_playlist_details(self):
        """
        Edit playlist detail :)
        """
        _id = self.get_id_of_playlist()
        headers = self.authorize_spotify_oAuth()
        base_url = "https://api.spotify.com/v1/playlists/"
        lookup_url = f"{base_url}{_id}"
        body = {"public": True}

        name = input("Write Playlist name for edit: ")
        description = input(f"Write description: ")

        self.__check_name_and_description(name)
        self.exists_name_of_playlist(self, name)
        self.__check_name_and_description(description)
        body['name'] = name
        body['description'] = description
        json_body = json.dumps(body)
        r = requests.put(lookup_url, data=json_body, headers=headers)
        if r.status_code not in range(200, 299):
            return "Something wrong."
        return "Successfully updated check out your Spotify playlist."
        

    # ADD ITEMS TO PLAYLIST
    def add_items_to_playlist(self, name, item_type = "track", limit = 10):
        """
        To add items to Playlist. Item type can be track or episode URIs
        """
        base_url = "https://api.spotify.com/v1/playlists/"
        _id = self.get_id_of_playlist()
        lookup_url = f"{base_url}{_id}/tracks"
        headers = self.authorize_spotify_oAuth()
        body = self.get_items(name, item_type, limit)
        r = requests.post(lookup_url, data=json.dumps(body), headers=headers)
        if r.status_code not in range(200, 299):
            return r.json()
        return f"Successfully added to playlist.\n{r.json()}"
    



    def get_items(self, name, search_type, limit):
        """
        return {"uris": ["spotify:track:4iV5W9uYEdYUVa79Axb7Rh",
                        "spotify:track:1301WleyT98MSxVHPZCA6M", 
                        "spotify:episode:512ojhOuo1ktJprKbVcKyQ"]
                }
        For add items to playlist :)
        """
        searched_items = self.search(name, search_type, limit=limit)
        ids = []
        items = searched_items[search_type + 's']['items']
        for item in items:
            ids.append(item['id'])
        urls = {}
        urls['uris'] = [f"spotify:{search_type}:{item_id}" for item_id in ids]
        return urls


    @classmethod
    def __check_name_and_description(cls, value):
        """
        This method is check name and description
        If checked is good then allow us to create Playlist of Spotify 
        """
        if not isinstance(value, str):
            raise TypeError("Playlist's name or description must be string")
        
        if value == '':
            raise Exception("You can't send empty for create Playlist")
    

    @classmethod
    def exists_name_of_playlist(cls, obj, value):
        names = obj.get_user_playlist_of_names()
        if value in names:
            raise ValueError(f"You already created {value}.Please add another name.!")

    
    def get_user_playlist_of_names(self):
        """
        return array [] of playlist's name
        """
        items = self.get_user_playlists()['items']
        names = []
        for item in items:
            names.append(item['name'])
        return names

    

    def get_id_of_playlist(self):
        """
        Return id of playlist 
        """
        names = self.get_user_playlist_of_names()
        items = self.get_user_playlists()['items']
        if not items:
            raise ValueError("You don't have playlist object.")
        print(f"Playlist Names: {names}")
        while True:
            user_answer = input("choice one to get info: ")
            if user_answer not in names:
                print("You writed incorrectly.")
                continue
            for item in items:
                if item['name'] == user_answer:
                    return item['id']


    

    # THIS IS SEARCH METHOD WE CAN SEARCH ITEMS FROM SPOTIFY
    def search(self, query, search_type = "artist", limit = 10):
        """
        return items of type ['artist', 'track', 'album', 'playlist', 'show', 'episode', 'audiobook']
        """
        headers = self.get_headers()
        endpoint = "https://api.spotify.com/v1/search"
        data = urlencode({"q": query, "type": search_type, "limit": limit}) # urlencode() => "q=value&search_type=value"
        lookup_url = f"{endpoint}?{data}"
        r = requests.get(lookup_url, headers=headers)
        if r.status_code != 200:
            return {}
        
        return r.json()

    



spo = SpotifyPlayList(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_USER_ID)

# ADD ITEMS TO PLAYLIST
#print(spo.add_items_to_playlist(name = "The Weeknd", limit=5))
# END ADD ITEMS TO PLAYLIST


# SEARCH
#print(spo.search("Rihanna", "episode", limit=3))
# END SEARCH
