import random

import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By

from languageschool.models import Language, Word, Score
from languageschool.tests.selenium.utils import assert_menu, authenticate


class TestVocabularyGameSelenium:
    def get_languages_for_setup(self):
        base_language = random.choice(Language.objects.all())
        target_language = random.choice(Language.objects.all().exclude(id=base_language.id))
        return base_language, target_language

    def get_synonym(self, word, language):
        for synonym in word.synonyms.all():
            if synonym.language.id == language.id:
                return synonym
        return None

    def select_languages(self, live_server, selenium_driver, base_language=None, target_language=None):
        selenium_driver.get(live_server.url + reverse("vocabulary-game-setup"))
        base_language_name = "default" if base_language is None else base_language.language_name
        target_language_name = "default" if target_language is None else target_language.language_name

        selenium_driver.find_element(By.ID, "selectBaseLanguage").click()
        selenium_driver.find_element(By.ID, base_language_name + "BaseLanguageItem").click()
        selenium_driver.find_element(By.ID, "selectTargetLanguage").click()
        selenium_driver.find_element(By.ID, target_language_name + "TargetLanguageItem").click()
        selenium_driver.find_element(By.ID, "submitButtonSetupForm").click()

    def input_answer(self, selenium_driver, correct_answer=None):
        is_correct = correct_answer is not None
        answer = correct_answer if is_correct else get_random_string(random.randint(5, 10))

        selenium_driver.find_element(By.ID, "translationWord").send_keys(answer)
        selenium_driver.find_element(By.ID, "answerSubmitButton").click()

        feedback_message = selenium_driver.find_element(By.CLASS_NAME,
                                                        "alert-success" if is_correct else "alert-danger")
        selenium_driver.find_element(By.ID, "newWordButton")

        return feedback_message.text

    @pytest.mark.django_db
    def test_vocabulary_game_setup_same_language(self, live_server, selenium_driver, vocabulary_game_dependencies):
        selenium_driver.get(live_server.url + reverse("vocabulary-game-setup"))

        language = random.choice(Language.objects.all())

        self.select_languages(live_server, selenium_driver, language, language)

        error_message = selenium_driver.find_element(By.CLASS_NAME, "alert-danger").text
        assert error_message == "The target and base languages must be different"
        assert_menu(selenium_driver, False)

    @pytest.mark.parametrize(
        "is_base_language_none, is_target_language_none, expected_message", [
            (True, True, "Please, select a base language"),
            (True, False, "Please, select a base language"),
            (False, True, "Please, select a target language")
        ]
    )
    @pytest.mark.django_db
    def test_vocabulary_game_setup_error(self, live_server, selenium_driver, article_game_dependencies,
                                         is_base_language_none, is_target_language_none, expected_message):
        base_language, target_language = self.get_languages_for_setup()

        if is_base_language_none:
            base_language = None
        if is_target_language_none:
            target_language = None

        self.select_languages(live_server, selenium_driver, base_language, target_language)
        error_message = selenium_driver.find_element(By.CLASS_NAME, "alert-danger").text
        assert error_message == expected_message
        assert_menu(selenium_driver, False)

    @pytest.mark.django_db
    def test_vocabulary_game_setup(self, live_server, selenium_driver, vocabulary_game_dependencies):
        selenium_driver.get(live_server.url + reverse("vocabulary-game-setup"))

        default_base_language_item = selenium_driver.find_elements(By.ID, "defaultBaseLanguageItem")
        default_target_language_item = selenium_driver.find_elements(By.ID, "defaultTargetLanguageItem")

        assert len(default_base_language_item) == 1
        assert len(default_target_language_item) == 1

        for language in Language.objects.all():
            base_language_item = selenium_driver.find_elements(By.ID, language.language_name + "BaseLanguageItem")
            target_language_item = selenium_driver.find_elements(By.ID, language.language_name + "TargetLanguageItem")
            assert len(base_language_item) == 1
            assert len(target_language_item) == 1

        assert_menu(selenium_driver, False)

    @pytest.mark.django_db
    def test_vocabulary_game(self, live_server, selenium_driver, vocabulary_game_dependencies):
        base_language, target_language = self.get_languages_for_setup()

        self.select_languages(live_server, selenium_driver, base_language, target_language)

        word_id = selenium_driver.find_element(By.ID, "wordId").get_attribute("value")
        base_language_input = selenium_driver.find_element(By.ID, "baseLanguage")
        word_name = selenium_driver.find_element(By.ID, "wordToTranslate").get_attribute("value")
        translation_inputs = selenium_driver.find_elements(By.ID, "translationWord")
        answer_submit_buttons = selenium_driver.find_elements(By.ID, "answerSubmitButton")

        word = Word.objects.get(pk=int(word_id))

        assert base_language_input.get_attribute("value") == base_language.language_name
        assert word.language.id == target_language.id
        assert word.word_name == word_name
        assert len(translation_inputs) == 1
        assert len(answer_submit_buttons) == 1
        assert_menu(selenium_driver, False)

    @pytest.mark.parametrize(
        "url_name", ["vocabulary-game", "vocabulary-game-verify-answer"]
    )
    @pytest.mark.django_db
    def test_vocabulary_game_without_setup(self, live_server, selenium_driver, vocabulary_game_dependencies, url_name):
        selenium_driver.get(live_server.url + reverse(url_name))
        assert selenium_driver.current_url == (live_server.url + reverse("vocabulary-game-setup"))
        assert_menu(selenium_driver, False)

    @pytest.mark.django_db
    def test_vocabulary_game_correct_answer(self, live_server, selenium_driver, vocabulary_game_dependencies):
        base_language, target_language = self.get_languages_for_setup()
        self.select_languages(live_server, selenium_driver, base_language, target_language)

        word_id = selenium_driver.find_element(By.ID, "wordId").get_attribute("value")

        word = Word.objects.get(pk=word_id)
        answer = self.get_synonym(word, base_language).word_name
        feedback_message = self.input_answer(selenium_driver, answer)

        assert feedback_message == "Correct :)\n" + str(word.word_name) + ": " + str(answer)
        assert_menu(selenium_driver, False)

    @pytest.mark.django_db
    def test_vocabulary_game_wrong_answer(self, live_server, selenium_driver, article_game_dependencies):
        base_language, target_language = self.get_languages_for_setup()
        self.select_languages(live_server, selenium_driver, base_language, target_language)

        word_id = selenium_driver.find_element(By.ID, "wordId").get_attribute("value")

        word = Word.objects.get(pk=word_id)
        answer = self.get_synonym(word, base_language).word_name
        feedback_message = self.input_answer(selenium_driver)

        assert feedback_message == 'Wrong answer\n' + str(word.word_name) + ": " + str(answer)
        assert_menu(selenium_driver, False)

    @pytest.mark.django_db
    def test_vocabulary_game_correct_answer_authenticated_user(self, live_server, selenium_driver,
                                                               vocabulary_game_dependencies, account, score):
        user, password = account()[0]
        vocabulary_game, words = vocabulary_game_dependencies
        score(users=[user], games=[vocabulary_game], languages=Language.objects.all())
        authenticate(live_server, selenium_driver, user, password)
        base_language, target_language = self.get_languages_for_setup()

        initial_score = Score.objects.filter(user=user, game=vocabulary_game, language=target_language).first().score

        self.select_languages(live_server, selenium_driver, base_language, target_language)

        word_id = selenium_driver.find_element(By.ID, "wordId").get_attribute("value")

        word = Word.objects.get(pk=word_id)
        answer = self.get_synonym(word, base_language).word_name
        feedback_message = self.input_answer(selenium_driver, answer)

        final_score = Score.objects.filter(user=user, game=vocabulary_game, language=target_language).first().score

        assert feedback_message == (
                "Correct :)\n" + str(word.word_name) + ": " + str(answer) + "\nYour score is " + str(initial_score + 1))
        assert final_score == (initial_score + 1)
        assert_menu(selenium_driver, True)

    @pytest.mark.django_db
    def test_vocabulary_game_wrong_answer_authenticated_user(self, live_server, selenium_driver,
                                                             vocabulary_game_dependencies, account, score):
        user, password = account()[0]
        vocabulary_game, words = vocabulary_game_dependencies
        score(users=[user], games=[vocabulary_game], languages=Language.objects.all())
        authenticate(live_server, selenium_driver, user, password)
        base_language, target_language = self.get_languages_for_setup()

        initial_score = Score.objects.filter(user=user, game=vocabulary_game, language=target_language).first().score

        self.select_languages(live_server, selenium_driver, base_language, target_language)

        word_id = selenium_driver.find_element(By.ID, "wordId").get_attribute("value")

        word = Word.objects.get(pk=word_id)
        feedback_message = self.input_answer(selenium_driver)
        correct_answer = self.get_synonym(word, base_language).word_name

        final_score = Score.objects.filter(user=user, game=vocabulary_game, language=target_language).first().score

        assert feedback_message == 'Wrong answer\n' + str(word.word_name) + ": " + str(correct_answer)
        assert final_score == initial_score
        assert_menu(selenium_driver, True)
