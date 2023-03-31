import base64
import requests
import datetime

"""
    Automate Spotify with Python
    
"""


class Spotify:
    token_url = "https://accounts.spotify.com/api/token"
    access_token = None
    access_token_expires = datetime.datetime.now()
    is_access_token_expired = True
    client_id = None
    client_secret = None
    
    
    def __init__(self, client_id, client_secret) -> None:
        self.client_id = client_id
        self.client_secret = client_secret

    
    
    def get_token_data(self):
        """
        This is token data for request body parameter
        """
        return {"grant_type": "client_credentials"}

    

    def get_client_credentials(self):
        """
        This method return a base64 encoded string
        """
        client_id = self.client_id
        client_secret = self.client_secret
        if client_id == None or client_secret == None:
            raise Exception("You must set client_id or client_secret")

        client_creden = f"{client_id}:{client_secret}"
        client_creden_base64_encoded_string = base64.b64encode(client_creden.encode())
        return client_creden_base64_encoded_string.decode()

    

    def get_token_headers(self):
        """
        return {"Authorization": "Basic <base64 encoded client_id:client_secret>"}
        """
        client_credentials_base64_decoded = self.get_client_credentials()
        return {
            "Authorization": f"Basic {client_credentials_base64_decoded}"
        }

    

    def get_json_data_by_perform_auth(self):
        """
        Get json data
        """
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()
        r = requests.post(token_url, data=token_data, headers=token_headers)
        if r.status_code != 200:
            raise Exception("Could not authenticate client.")
        
        data = r.json()
        now = datetime.datetime.now()
        access_token = data['access_token']
        expires_in = data['expires_in'] # seconds 3600 => 1 HOUR

        expires = now + datetime.timedelta(seconds=expires_in)
        
        # CLASS'S ATTRIBUTE SET UP
        self.access_token = access_token
        self.access_token_expires = expires
        self.is_access_token_expired = expires < now
        return True


    
    def get_access_token(self):
        """
        GET ACCESS TOKEN
        return your token 
        """
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()

        if expires < now:
            """
            When access token's time expired so again post request to get access token
            """
            self.get_json_data_by_perform_auth()
            return self.get_access_token()
        
        elif token == None:
            self.get_json_data_by_perform_auth()
            return self.get_access_token()
        return token

    

    def get_headers(self):
        """
        return {"Authorization": f"Bearer {your access token}"}
        """
        access_token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        return headers
