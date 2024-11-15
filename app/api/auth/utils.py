from typing import Tuple

import secrets
import requests
from urllib.parse import urlencode

from flask import current_app

def generate_random_state() -> str:
    return secrets.token_hex(16)

def fetch_access_token(url: str) -> str | None:
    r = requests.post(url)
    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        current_app.logger.info(f"Failed requesting user info from Fenix. {e}")
        return None

    if r.status_code != 200:
        current_app.logger.info(f"Failed fetching access token from Fenix. Status Code {r.status_code}")
        return None

    access_token: str
    try:
        access_token = r.json()['access_token']
    except requests.exceptions.JSONDecodeError as e:
        current_app.logger.info(f"Access token fetch response from Fenix is not JSON. {e}")
        return None
    except TypeError as e:
        current_app.logger.info(f"Unknown response type. {e}")
        return None
    except KeyError:
        current_app.logger.info(f"Missing access token key in Fenix response. {e}")
        return None
    except Exception:
        return None

    return access_token 

def get_user_ist_id(access_token: str) -> str | None:
    r = requests.get(
        "https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person?" + urlencode({"access_token": access_token})
    )
    try:
        r.raise_for_status()
    except requests.httperror as e:
        current_app.logger.info(f"Failed requesting user info from Fenix. {e}")
        return None
    except Exception:
        return None

    if r.status_code != 200:
        current_app.logger.info(f"Failed requesting user info from Fenix. Status Code {r.status_code}")
        return None

    ist_id: dict 
    try:
        ist_id = r.json()['username']
    except requests.exceptions.JSONDecodeError as e:
        current_app.logger.info(f"User info response from fenix is not JSON. {e}")
        return None
    except TypeError as e:
        current_app.logger.info(f"Unknown response type. {e}")
        return None
    except KeyError:
        current_app.logger.info(f"Missing access token key in Fenix response. {e}")
        return None

    return ist_id
