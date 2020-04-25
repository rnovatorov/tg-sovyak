import gzip

import pytest

from sovyak import package


PACK_NAME = "russv07.6"


class TestChgkDB:
    @pytest.fixture(scope="class")
    def pack(self, resources):
        with gzip.open(resources / f"{PACK_NAME}.html.gzip") as markup:
            yield package.chgk_db.parse(PACK_NAME, markup)

    def test_pack_name(self, pack):
        assert pack.name == PACK_NAME

    def test_pack_len(self, pack):
        assert len(pack) == 12

    def test_theme_info(self, pack):
        theme = pack.themes[4]
        assert theme.info == "Американские экспедиции на Луну"

    def test_themes_len(self, pack):
        for theme in pack:
            assert len(theme) == 5

    def test_questions_non_empty(self, pack):
        for theme in pack:
            for question in theme:
                assert question.text
                assert question.answer

    def test_question_text(self, pack):
        question = pack.themes[4].questions[2]
        assert (
            question.text
            == 'На "Аполлоне-12" ОНИ назывались "Янки Клиппер" и "Интрепид".'
        )
        assert question.answer == "Орбитальный блок и лунная кабина."
