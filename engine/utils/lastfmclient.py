import requests
from requests.exceptions import JSONDecodeError

from config import Config


class LastFMClient:
    API_KEY = Config.API_KEY_LAST_FM
    BASE_URL = 'http://ws.audioscrobbler.com/2.0/?'

    @staticmethod
    def make_lastfm_request(params: dict) -> dict:
        params['api_key'] = LastFMClient.API_KEY
        params['format'] = 'json'

        response = requests.get(LastFMClient.BASE_URL, params=params)

        if response.status_code == 200:
            try:
                return response.json()
            except JSONDecodeError:
                print("JSON decoding error")
                return {}
        else:
            print('API Error:', response.status_code, response.text)
            return {}
