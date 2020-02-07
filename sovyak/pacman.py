import re

import asks
import bs4
import more_itertools as mit

from . import chgk


DB_URL = "https://db.chgk.info/tour"
THEME_SIZE = 5
RE_INFO = re.compile(r"[\w\-,]+")


async def download(name):
    pack = chgk.Pack(name=name)

    url = f"{DB_URL}/{name}/print"
    response = await asks.get(url)
    soup = bs4.BeautifulSoup(response.text, "lxml")

    for div in soup.find_all("div", style="margin-top:20px;"):
        info = " ".join(RE_INFO.findall(div.contents[1]))
        theme = chgk.Theme(info=info)

        ps = div.find_all("p")
        qa = mit.take(THEME_SIZE, mit.chunked(ps, 2))

        for q, a in qa:
            question = chgk.Question(text=q.text, answer=a.text)
            theme.questions.append(question)

        pack.themes.append(theme)

    if not pack.themes:
        raise ValueError("Themes not found")

    return pack
