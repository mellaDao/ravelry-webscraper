# ravelry_auth.py
import re

import requests
from bs4 import BeautifulSoup
from encrypt_password import load_credentials

from my_constants import HEADERS, BASE_URL, LOGIN_URL

def load_credentials_from_file(path=None, key=None):
    return load_credentials(path=path, key=key)

def create_session(username, password):
    session = requests.Session()
    login_page = session.get(LOGIN_URL, headers=HEADERS)
    soup = BeautifulSoup(login_page.text, "html.parser")

    csrf_token = soup.find("input", {"name": "authenticity_token"})
    if not csrf_token:
        raise RuntimeError("CSRF token not found on Ravelry login page.")

    payload = {
        "user[login]": username,
        "user[password]": password,
        "authenticity_token": csrf_token["value"],
    }
    session.post(LOGIN_URL, data=payload, headers=HEADERS)
    verify_session(session)
    return session


def verify_session(session):
    response = session.get(BASE_URL, headers=HEADERS, timeout=60)
    soup = BeautifulSoup(response.text, "html.parser")

    if soup.find("a", href=re.compile(r"/account/logout")):
        return True
    
    print(response.text[:2000])  # TEMP DEBUG
    raise RuntimeError("Login failed. Check username and password.")