# ravelry_auth.py
import re

import requests
from bs4 import BeautifulSoup
from encrypt_password import load_credentials

HEADERS = {"User-Agent": "Mozilla/5.0"}
LOGIN_URL = "https://www.ravelry.com/account/login"


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
    response = session.get("https://www.ravelry.com/", headers=HEADERS, timeout=60)
    soup = BeautifulSoup(response.text, "html.parser")

    if soup.find("a", href=re.compile(r"/account/logout")):
        return True
    
    print(response.text[:2000])  # TEMP DEBUG
    raise RuntimeError("Login failed. Check username and password.")