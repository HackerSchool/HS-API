import logging

from typing import Dict

import requests
from requests.exceptions import HTTPError
from requests.exceptions import JSONDecodeError

from urllib.parse import urlencode

logger = logging.getLogger(__name__)

class FenixService:
    def __init__(self, *, client_id: str, client_secret: str, root_uri: str, redirect_endpoint: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.root_uri = root_uri
        self.redirect_endpoint = redirect_endpoint

    def redirect_url(self, state: str):
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.root_uri + self.redirect_endpoint,
            "state": state,
        }
        return "https://fenix.tecnico.ulisboa.pt/oauth/userdialog?" + urlencode(params)

    def fetch_access_token(self, *, redirect_endpoint: str, code: str) -> str:
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.root_uri + redirect_endpoint,
            "grant_type": "authorization_code",
            "code": code,
        }
        rsp = requests.post("https://fenix.tecnico.ulisboa.pt/oauth/access_token?" + urlencode(params))
        try:
            rsp.raise_for_status()
            access_token = rsp.json()["access_token"]
        except HTTPError as e:
            logging.error(f"Content: {rsp.content}")
            raise ValueError(f"Failed fetching access token from Fénix: {e}")
        except (JSONDecodeError, KeyError) as e:
            logging.error(str(e))
            raise ValueError(f"Failed fetching access token from Fénix: {e}")

        return access_token

    def fetch_user_info(self, access_token: str) -> Dict[str, str]:
        rsp = requests.get("https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person?" + urlencode({"access_token": access_token}))
        try:
            rsp.raise_for_status()
            rsp_json = rsp.json()
        except HTTPError as e:
            logging.error(f"Content: {rsp.content}")
            raise ValueError(f"Failed fetching user information from Fénix: {e}")
        except Exception as e:
            logging.error(str(e))
            raise ValueError(f"Failed fetching user information from Fénix: {e}")

        return rsp_json
