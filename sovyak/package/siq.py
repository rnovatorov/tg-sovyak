import bs4

from .pack import Pack
from .question import Question
from .theme import Theme


def parse_siq(markup):
    soup = bs4.BeautifulSoup(markup, "lxml")

    package_tag = soup.find("package")
    if package_tag is None:
        raise ValueError(f"package not found: {soup}")

    return parse_package(package_tag)


def parse_package(tag):
    try:
        name = tag["name"]
    except KeyError:
        raise ValueError(f"unnamed pack: {tag}") from None

    theme_tags = tag.find_all("theme")
    if not theme_tags:
        raise ValueError(f"no themes found: {tag}")

    themes = [parse_theme(tag) for tag in theme_tags]
    return Pack(name=name, themes=themes)


def parse_theme(tag):
    try:
        name = tag["name"]
    except KeyError:
        raise ValueError(f"unnamed theme: {tag}") from None

    question_tags = tag.find_all("question")
    if not question_tags:
        raise ValueError(f"empty theme: {tag}")

    questions = [parse_question(tag) for tag in question_tags]
    return Theme(info=name, questions=questions)


def parse_question(tag):
    scenario_tag = tag.find("scenario")
    if scenario_tag is None:
        raise ValueError(f"question with no scenario: {tag}")

    answer_tag = tag.find("answer")
    if answer_tag is None:
        raise ValueError(f"question with no answer: {tag}")

    text = parse_scenario(scenario_tag)
    answer = parse_answer(answer_tag)
    return Question(text=text, answer=answer)


def parse_scenario(tag):
    text = tag.get_text().strip()
    if not text:
        raise ValueError(f"scenario with no text: {tag}")

    return text


def parse_answer(tag):
    text = tag.get_text().strip()
    if not text:
        raise ValueError(f"answer with no text: {tag}")

    return text
