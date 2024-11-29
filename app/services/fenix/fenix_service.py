from typing import Tuple, Optional

import requests

from urllib.parse import urlencode

from flask import current_app

from .exceptions import FenixException

__client_id = None
__client_secret = None
__fenix_redirect_url = None

def init_app(app):
    global __client_id, __client_secret, __fenix_redirect_url
    __client_id = app.config.get("CLIENT_ID", "")
    __client_secret = app.config.get("CLIENT_SECRET", "")
    __fenix_redirect_url = app.config.get("FENIX_REDIRECT_URL")

def client_id() -> str:
    return __client_id

def client_secret() -> str:
    return __client_secret

def redirect_url() -> str:
    return __fenix_redirect_url

def is_not_implemented():
    return not __client_id or not __client_secret or not __fenix_redirect_url

def exchange_access_token(code: str) -> str | None:
    params = {
        "client_id": __client_id,
        "client_secret": __client_secret,
        "redirect_uri": __fenix_redirect_url,
        "code": code,
        "grant_type": "authorization_code"
    }
    r = requests.post("https://fenix.tecnico.ulisboa.pt/oauth/access_token?" + urlencode(params))
    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        current_app.logger.debug(f"exchange_access_token: raise_for_status: {e}")
        raise FenixException("Failed fetching user info from Fenix")

    if r.status_code != 200:
        current_app.logger.info(f"exchange_access_token: status_code = {r.status_code}")
        raise FenixException(f"Failed decoding Fenix response getting access token")

    access_token: str
    try:
        access_token = r.json()['access_token']
    except requests.exceptions.JSONDecodeError as e:
        current_app.logger.debug(f"exchange_access_token: decoding error: {e}")
        raise FenixException(f"Failed decoding Fenix response getting access token")
    except TypeError as e:
        current_app.logger.debug(f"exchange_access_token: unknown response type: {e}")
        raise FenixException("Failed exhancing access token from  Fenix")
    except KeyError:
        current_app.logger.debug(f"exchange_access_token: missing keys: {e}")
        raise FenixException("Failed exhancing access token from  Fenix")

    return access_token 

def get_user_info(access_token: str) -> Tuple[str, str, str]:
    r = requests.get(
        "https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person?" + urlencode({"access_token": access_token})
    )
    try:
        r.raise_for_status()
    except requests.httperror as e:
        current_app.logger.debug(f"get_user_info: raise_for_status: {e}")
        raise FenixException("Failed fetching user info from Fenix")

    if r.status_code != 200:
        current_app.logger.info(f"get_user_info: status_code = {r.status_code}")
        raise FenixException("Failed fetching user info from Fenix")

    ist_id: dict 
    name: str
    try:
        ist_id, name, email = r.json()['username'], r.json()['name'], r.json()['email']
    except requests.exceptions.JSONDecodeError as e:
        current_app.logger.debug(f"get_user_info: decoding error: {e}")
        raise FenixException("Failed decoding user info from Fenix")
    except TypeError as e:
        current_app.logger.debug(f"get_user_info: unknown response type: {e}")
        raise FenixException("Failed decoding user info from Fenix")
    except KeyError:
        current_app.logger.debug(f"get_user_info: missing keys: {e}")
        raise FenixException("Failed decoding user info from Fenix")

    return True, ist_id, name, email
