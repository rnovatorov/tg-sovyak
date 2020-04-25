import pytest

from sovyak import package


PACK_NAME = "Domovina Open 1.6"


class TestChgkDB:
    @pytest.fixture(scope="class")
    def pack(self, resources):
        return package.siq.load(resources / f"{PACK_NAME}.siq")

    def test_pack_name(self, pack):
        assert pack.name == PACK_NAME

    def test_pack_len(self, pack):
        assert len(pack) == 15

    def test_theme_info(self, pack):
        theme = pack.themes[4]
        assert theme.info == "Болезни"

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
            == "Четвёртое представление этой комедии-балета стало последним для автора и исполнителя главной роли - Мольера. Вечером после спектакля он умер"
        )
        assert question.answer == "Мнимый больной"
