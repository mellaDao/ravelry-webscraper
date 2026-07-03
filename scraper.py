import math
import re
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup

from ravelry_auth import HEADERS, create_session, load_credentials_from_file

CARDS_PER_PAGE = 32


def _people_gallery_url(pattern_slug, page):
    return (
        f"https://www.ravelry.com/patterns/library/{pattern_slug}/people"
        f"?page={page}&view=cards"
    )


def get_project_count(session, pattern_slug):
    response = session.get(_people_gallery_url(pattern_slug, 1), headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    people_tab = soup.find("span", id="people_tab")

    if not people_tab:
        raise RuntimeError(
            f"Could not find project count for pattern '{pattern_slug}'. "
            "Check the slug or login status."
        )

    match = re.search(r"\((\d+)\)", people_tab.get_text(strip=True))
    if not match:
        raise RuntimeError(f"Could not parse project count for pattern '{pattern_slug}'.")

    return int(match.group(1))


def _parse_project_card(card, session):
    title_block = card.find("div", class_="notebook_card__title")
    if not title_block:
        return None

    link = title_block.find("a")
    if not link or not link.get("href"):
        return None

    project_url = link["href"]
    if project_url.startswith("/"):
        project_url = f"https://www.ravelry.com{project_url}"

    username = link.get_text(strip=True) if link else ""
    username = username.split("'s")[0]

    yarn_name = card.find("div", class_="notebook_card__yarn_name")
    yarn_colorway = card.find("div", class_="notebook_card__yarn_colorway")

    status_block = card.find("div", class_="notebook_card__status")
    status_text = ""
    date = ""
    if status_block:
        status = status_block.find("span")
        status_text = status.get_text(strip=True) if status else ""
        full_text = status_block.get_text(separator=" ", strip=True)
        date = full_text.replace(status_text, "").strip() if status_text else ""
        date = date.replace("\n", " ").strip()

    response = session.get(project_url, headers=HEADERS)
    notes_soup = BeautifulSoup(response.text, "html.parser")
    notes = notes_soup.find("div", class_="notes markdown core_item_content__text_block")

    full_project_notes = ""
    if notes:
        note_texts = [paragraph.get_text(strip=True) for paragraph in notes.find_all("p")]
        full_project_notes = " ".join(note_texts)

    return {
        "username": username,
        "yarn_name": yarn_name.get_text(strip=True) if yarn_name else "",
        "yarn_colorway": yarn_colorway.get_text(strip=True) if yarn_colorway else "",
        "project_notes": full_project_notes,
        "status": status_text,
        "date": date,
        "url": project_url,
    }


def scrape_pattern(
    pattern_slug,
    username=None,
    password=None,
    credentials_path=None,
    credentials_key=None,
    session=None,
    on_progress=None,
):
    if session is None:
        if not username or not password:
            username, password = load_credentials_from_file(
                path=credentials_path,
                key=credentials_key,
            )
        session = create_session(username, password)
    num_projects = get_project_count(session, pattern_slug)
    num_pages = int(math.ceil(num_projects / float(CARDS_PER_PAGE)))

    if on_progress:
        on_progress(f"Found {num_projects} projects across {num_pages} pages.")

    rows = []
    for page in range(1, num_pages + 1):
        if on_progress:
            on_progress(f"Scraping page {page} of {num_pages}...")

        response = session.get(_people_gallery_url(pattern_slug, page), headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")

        for card in soup.find_all("div", class_="notebook_card__main"):
            row = _parse_project_card(card, session)
            if row:
                rows.append(row)

        if on_progress:
            on_progress(f"Collected {len(rows)} projects so far.")

    df = pd.DataFrame(rows)
    df["project_notes"] = df["project_notes"].fillna("")
    return df