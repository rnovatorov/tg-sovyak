import re

import asks
import bs4
import more_itertools as mit

from .pack import Pack
from .question import Question
from .theme import Theme


DB_URL = "https://db.chgk.info/tour"
THEME_SIZE = 5
RE_INFO = re.compile(r"[\w\-,]+")


async def download(name):
    url = f"{DB_URL}/{name}/print"
    response = await asks.get(url)
    soup = bs4.BeautifulSoup(response.text, "lxml")
    return parse_package(name, soup)


def parse_package(name, soup):
    divs = soup.find_all("div", style="margin-top:20px;")
    if not divs:
        raise ValueError(f"no themes found: {soup}")

    themes = [parse_theme(div) for div in divs]
    return Pack(name=name, themes=themes)


def parse_theme(div):
    info = " ".join(RE_INFO.findall(div.contents[1]))
    if not info:
        raise ValueError(f"theme with no info: {div}")

    ps = div.find_all("p")
    qas = mit.take(THEME_SIZE, mit.chunked(ps, 2))

    questions = [parse_question(q, a) for q, a in qas]
    return Theme(info=info, questions=questions)


def parse_question(q, a):
    text = q.text.strip()
    if not text:
        raise ValueError(f"question with no text: {q}")

    answer = a.text.strip()
    if not answer:
        raise ValueError(f"question with no answer: {a}")

    return Question(text=text, answer=answer)
