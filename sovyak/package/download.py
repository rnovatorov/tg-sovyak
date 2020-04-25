import re

import asks
import bs4
import more_itertools as mit

from .pack import Pack
from .question import Question
from .theme import Theme


DB_URL = "https://db.chgk.info/tour"


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


RE_INFO = re.compile(r"[\w\-,]+")
THEME_SIZE = 5


def parse_theme(div):
    info = " ".join(RE_INFO.findall(div.contents[1]))
    if not info:
        raise ValueError(f"theme with no info: {div}")

    ps = div.find_all("p")
    qas = mit.take(THEME_SIZE, mit.chunked(ps, 2))

    questions = [parse_question(q, a) for q, a in qas]
    return Theme(info=info, questions=questions)


RE_QUESTION = re.compile(r"^\d+\. (.+?)\.?$")
RE_ANSWER = re.compile(r"^Ответ: (.+?)\.?$")


def parse_question(q, a):
    text_match = RE_QUESTION.match(q.text.strip().replace("\n", " "))
    if text_match is None:
        raise ValueError(f"cannot match question: {q}")
    (text,) = text_match.groups()

    answer_match = RE_ANSWER.match(a.text.strip().replace("\n", " "))
    if answer_match is None:
        raise ValueError(f"cannot match answer: {a}")
    (answer,) = answer_match.groups()

    return Question(text=text, answer=answer)
