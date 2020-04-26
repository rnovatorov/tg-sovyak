import zipfile

import bs4

from .pack import Pack
from .question import Question
from .theme import Theme


def load(file):
    with zipfile.ZipFile(file) as archive:
        with archive.open("content.xml") as siq:
            return parse(siq)


def parse(markup):
    soup = bs4.BeautifulSoup(markup, "lxml-xml")

    package_tag = soup.find("package")
    if package_tag is None:
        raise ValueError(f"package not found: {soup}")

    return parse_package(package_tag)


def parse_package(tag):
    try:
        name = tag["name"]
    except KeyError:
        raise ValueError(f"pack with no name: {tag}") from None

    theme_tags = tag.find_all("theme")
    if not theme_tags:
        raise ValueError(f"pack with no themes: {tag}")

    themes = [parse_theme(tag) for tag in theme_tags]
    return Pack(name=name, themes=themes)


def parse_theme(tag):
    try:
        name = tag["name"]
    except KeyError:
        raise ValueError(f"theme with no name: {tag}") from None

    question_tags = tag.find_all("question")
    if not question_tags:
        raise ValueError(f"theme with no questions: {tag}")

    questions = [parse_question(tag, theme_name=name) for tag in question_tags]
    return Theme(info=name, questions=questions)


def parse_question(tag, theme_name):
    scenario_tag = tag.find("scenario")
    if scenario_tag is None:
        raise ValueError(f"question with no scenario: {tag}")

    text = parse_scenario(scenario_tag)

    new_theme = parse_question_type(tag.find("type"))
    if new_theme is not None and new_theme != theme_name:
        text = f"[{new_theme}] {text}"

    answer_tag = tag.find("answer")
    if answer_tag is None:
        raise ValueError(f"question with no answer: {tag}")

    answer = parse_answer(answer_tag)

    return Question(text=text, answer=answer)


def parse_question_type(tag):
    if tag is None:
        return None

    try:
        type_ = tag["name"]
    except KeyError:
        raise ValueError(f"question type with no name: {tag}")

    if type_ not in ["cat", "bagcat"]:
        return None

    for param_tag in tag.find_all("param"):
        name, value = parse_question_type_param(param_tag)
        if name == "theme":
            return value

    raise ValueError(f"question of cat type without theme: {tag}")


def parse_question_type_param(tag):
    try:
        name = tag["name"]
    except KeyError:
        raise ValueError(f"question type param with no name: {tag}")

    value = tag.get_text().strip()
    if not value:
        raise ValueError(f"question type param with no value: {tag}")

    return name, value


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
