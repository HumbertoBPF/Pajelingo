import random

import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By

from languageschool.models import Word, Language, Score
from languageschool.tests.selenium.utils import assert_menu, authenticate


class TestArticleGameSelenium:
    def get_language_for_setup(self):
        return random.choice(Language.objects.all().exclude(language_name="English"))

    def select_language(self, live_server, selenium_driver, language=None):
        selenium_driver.get(live_server.url + reverse("article-game-setup"))

        language_name = "default" if language is None else language.language_name

        selenium_driver.find_element(By.ID, "selectLanguage").click()
        selenium_driver.find_element(By.ID, language_name + "Item").click()
        selenium_driver.find_element(By.ID, "submitButtonSetupForm").click()

    def input_answer(self, selenium_driver, correct_answer=None):
        is_correct = correct_answer is not None
        answer = correct_answer if is_correct else get_random_string(random.randint(5, 10))

        selenium_driver.find_element(By.ID, "article").send_keys(answer)
        selenium_driver.find_element(By.ID, "answerSubmitButton").click()

        feedback_message = selenium_driver.find_element(By.CLASS_NAME, "alert-success" if is_correct else "alert-danger")
        selenium_driver.find_element(By.ID, "newWordButton")

        return feedback_message.text

    @pytest.mark.django_db
    def test_article_game_setup(self, live_server, selenium_driver, article_game_dependencies):
        selenium_driver.get(live_server.url + reverse("article-game-setup"))

        option_items = selenium_driver.find_elements(By.ID, "defaultItem")
        assert len(option_items) == 1

        for language in Language.objects.all():
            if language.language_name != "English":
                option_items = selenium_driver.find_elements(By.ID, language.language_name+"Item")
                assert len(option_items) == 1

        assert_menu(selenium_driver, False)

    @pytest.mark.django_db
    def test_article_game_setup_error(self, live_server, selenium_driver, article_game_dependencies):
        self.select_language(live_server, selenium_driver)
        error_message = selenium_driver.find_element(By.CLASS_NAME, "alert-danger").text
        assert error_message == "You must choose a language"
        assert_menu(selenium_driver, False)

    @pytest.mark.django_db
    def test_article_game(self, live_server, selenium_driver, article_game_dependencies):
        language = self.get_language_for_setup()
        self.select_language(live_server, selenium_driver, language)

        word_id = selenium_driver.find_element(By.ID, "wordId").get_attribute("value")
        word_name = selenium_driver.find_element(By.ID, "word").get_attribute("value")
        article_inputs = selenium_driver.find_elements(By.ID, "article")
        answer_submit_buttons = selenium_driver.find_elements(By.ID, "answerSubmitButton")

        word = Word.objects.get(pk=int(word_id))

        assert word.language.id == language.id
        assert word.word_name == word_name
        assert len(article_inputs) == 1
        assert len(answer_submit_buttons) == 1
        assert_menu(selenium_driver, False)

    @pytest.mark.django_db
    def test_article_game_without_setup(self, live_server, selenium_driver, article_game_dependencies):
        selenium_driver.get(live_server.url + reverse("article-game"))
        assert selenium_driver.current_url == (live_server.url + reverse("article-game-setup"))
        assert_menu(selenium_driver, False)

    @pytest.mark.django_db
    def test_article_game_correct_answer(self, live_server, selenium_driver, article_game_dependencies):
        self.select_language(live_server, selenium_driver, self.get_language_for_setup())

        word_id = selenium_driver.find_element(By.ID, "wordId").get_attribute("value")

        word = Word.objects.get(pk=word_id)
        feedback_message = self.input_answer(selenium_driver, word.article.article_name)

        assert feedback_message == "Correct :)\n" + str(word)
        assert_menu(selenium_driver, False)

    @pytest.mark.django_db
    def test_article_game_wrong_answer(self, live_server, selenium_driver, article_game_dependencies):
        self.select_language(live_server, selenium_driver, self.get_language_for_setup())

        word_id = selenium_driver.find_element(By.ID, "wordId").get_attribute("value")

        word = Word.objects.get(pk=word_id)
        feedback_message = self.input_answer(selenium_driver)

        assert feedback_message == 'Wrong answer\n' + str(word)
        assert_menu(selenium_driver, False)

    @pytest.mark.django_db
    def test_article_game_correct_answer_authenticated_user(self, live_server, selenium_driver, article_game_dependencies, account, score):
        user, password = account()[0]
        article_game, words = article_game_dependencies
        score(users=[user], games=[article_game], languages=Language.objects.all())
        authenticate(live_server, selenium_driver, user.username, password)
        language = self.get_language_for_setup()

        initial_score = Score.objects.filter(user=user, game=article_game, language=language).first().score

        self.select_language(live_server, selenium_driver, language)

        word_id = selenium_driver.find_element(By.ID, "wordId").get_attribute("value")

        word = Word.objects.get(pk=word_id)
        feedback_message = self.input_answer(selenium_driver, word.article.article_name)

        final_score = Score.objects.filter(user=user, game=article_game, language=language).first().score

        assert feedback_message == ("Correct :)\n" + str(word) + "\nYour score is " + str(initial_score + 1))
        assert final_score == (initial_score + 1)
        assert_menu(selenium_driver, True)

    @pytest.mark.django_db
    def test_article_game_wrong_answer_authenticated_user(self, live_server, selenium_driver,
                                                            article_game_dependencies, account, score):
        user, password = account()[0]
        article_game, words = article_game_dependencies
        score(users=[user], games=[article_game], languages=Language.objects.all())
        authenticate(live_server, selenium_driver, user.username, password)
        language = self.get_language_for_setup()

        initial_score = Score.objects.filter(user=user, game=article_game, language=language).first().score

        self.select_language(live_server, selenium_driver, language)

        word_id = selenium_driver.find_element(By.ID, "wordId").get_attribute("value")

        word = Word.objects.get(pk=word_id)
        feedback_message = self.input_answer(selenium_driver)

        final_score = Score.objects.filter(user=user, game=article_game, language=language).first().score

        assert feedback_message == 'Wrong answer\n' + str(word)
        assert final_score == initial_score
        assert_menu(selenium_driver, True)
