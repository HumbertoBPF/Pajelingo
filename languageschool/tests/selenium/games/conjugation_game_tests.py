import random

import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By

from languageschool.models import Language, Word, Conjugation, Score
from languageschool.tests.selenium.utils import assert_menu, authenticate


class TestConjugationGameSelenium:
    def get_language_for_setup(self):
        return random.choice(Language.objects.all())

    def select_language(self, live_server, selenium_driver, language=None):
        selenium_driver.get(live_server.url + reverse("conjugation-game-setup"))

        language_name = "default" if language is None else language.language_name

        selenium_driver.find_element(By.ID, "selectLanguage").click()
        selenium_driver.find_element(By.ID, language_name + "Item").click()
        selenium_driver.find_element(By.ID, "submitButtonSetupForm").click()

    def input_answer(self, selenium_driver, correct_answer=None):
        is_correct = correct_answer is not None
        answer_1 = correct_answer[0] if is_correct else get_random_string(random.randint(5, 10))
        answer_2 = correct_answer[1] if is_correct else get_random_string(random.randint(5, 10))
        answer_3 = correct_answer[2] if is_correct else get_random_string(random.randint(5, 10))
        answer_4 = correct_answer[3] if is_correct else get_random_string(random.randint(5, 10))
        answer_5 = correct_answer[4] if is_correct else get_random_string(random.randint(5, 10))
        answer_6 = correct_answer[5] if is_correct else get_random_string(random.randint(5, 10))

        selenium_driver.find_element(By.ID, "conjugation_1").send_keys(answer_1)
        selenium_driver.find_element(By.ID, "conjugation_2").send_keys(answer_2)
        selenium_driver.find_element(By.ID, "conjugation_3").send_keys(answer_3)
        selenium_driver.find_element(By.ID, "conjugation_4").send_keys(answer_4)
        selenium_driver.find_element(By.ID, "conjugation_5").send_keys(answer_5)
        selenium_driver.find_element(By.ID, "conjugation_6").send_keys(answer_6)
        selenium_driver.find_element(By.ID, "answerSubmitButton").click()

        feedback_message = selenium_driver.find_element(By.CLASS_NAME,
                                                        "alert-success" if is_correct else "alert-danger")
        selenium_driver.find_element(By.ID, "newWordButton")

        return feedback_message.text

    @pytest.mark.django_db
    def test_conjugation_game_setup(self, live_server, selenium_driver, conjugation_game_dependencies):
        selenium_driver.get(live_server.url + reverse("conjugation-game-setup"))

        option_items = selenium_driver.find_elements(By.ID, "defaultItem")
        assert len(option_items) == 1

        for language in Language.objects.all():
            option_items = selenium_driver.find_elements(By.ID, language.language_name + "Item")
            assert len(option_items) == 1

        assert_menu(selenium_driver, False)

    @pytest.mark.django_db
    def test_conjugation_game_setup_error(self, live_server, selenium_driver, conjugation_game_dependencies):
        self.select_language(live_server, selenium_driver)
        error_message = selenium_driver.find_element(By.CLASS_NAME, "alert-danger").text
        assert error_message == "You must choose a language"
        assert_menu(selenium_driver, False)

    @pytest.mark.django_db
    def test_conjugation_game(self, live_server, selenium_driver, conjugation_game_dependencies):
        language = self.get_language_for_setup()
        self.select_language(live_server, selenium_driver, language)

        word_id = selenium_driver.find_element(By.ID, "wordId").get_attribute("value")
        tense_inputs = selenium_driver.find_elements(By.ID, "tense")
        conjugation_1_inputs = selenium_driver.find_elements(By.ID, "conjugation_1")
        conjugation_2_inputs = selenium_driver.find_elements(By.ID, "conjugation_2")
        conjugation_3_inputs = selenium_driver.find_elements(By.ID, "conjugation_3")
        conjugation_4_inputs = selenium_driver.find_elements(By.ID, "conjugation_4")
        conjugation_5_inputs = selenium_driver.find_elements(By.ID, "conjugation_5")
        conjugation_6_inputs = selenium_driver.find_elements(By.ID, "conjugation_6")
        answer_submit_buttons = selenium_driver.find_elements(By.ID, "answerSubmitButton")

        word = Word.objects.get(pk=int(word_id))

        assert word.language.id == language.id
        assert len(tense_inputs) == 1
        assert len(conjugation_1_inputs) == 1
        assert len(conjugation_2_inputs) == 1
        assert len(conjugation_3_inputs) == 1
        assert len(conjugation_4_inputs) == 1
        assert len(conjugation_5_inputs) == 1
        assert len(conjugation_6_inputs) == 1
        assert len(answer_submit_buttons) == 1
        assert_menu(selenium_driver, False)

    @pytest.mark.parametrize(
        "url_name", ["conjugation-game", "conjugation-game-verify-answer"]
    )
    @pytest.mark.django_db
    def test_conjugation_game_without_setup(self, live_server, selenium_driver, conjugation_game_dependencies,
                                            url_name):
        selenium_driver.get(live_server.url + reverse(url_name))
        assert selenium_driver.current_url == (live_server.url + reverse("conjugation-game-setup"))
        assert_menu(selenium_driver, False)

    @pytest.mark.django_db
    def test_conjugation_game_correct_answer(self, live_server, selenium_driver, conjugation_game_dependencies):
        language = self.get_language_for_setup()
        self.select_language(live_server, selenium_driver, language)

        word_id = selenium_driver.find_element(By.ID, "wordId").get_attribute("value")
        tense = selenium_driver.find_element(By.ID, "tense").get_attribute("value")

        conjugation = Conjugation.objects.filter(word=word_id, tense=tense).first()
        answer = [conjugation.conjugation_1, conjugation.conjugation_2, conjugation.conjugation_3,
                  conjugation.conjugation_4, conjugation.conjugation_5, conjugation.conjugation_6]
        feedback_message = self.input_answer(selenium_driver, answer)

        assert feedback_message == "Correct :)\n" + \
               language.personal_pronoun_1 + " " + conjugation.conjugation_1 + "\n" + \
               language.personal_pronoun_2 + " " + conjugation.conjugation_2 + "\n" + \
               language.personal_pronoun_3 + " " + conjugation.conjugation_3 + "\n" + \
               language.personal_pronoun_4 + " " + conjugation.conjugation_4 + "\n" + \
               language.personal_pronoun_5 + " " + conjugation.conjugation_5 + "\n" + \
               language.personal_pronoun_6 + " " + conjugation.conjugation_6
        assert_menu(selenium_driver, False)

    @pytest.mark.django_db
    def test_conjugation_game_wrong_answer(self, live_server, selenium_driver, conjugation_game_dependencies):
        language = self.get_language_for_setup()
        self.select_language(live_server, selenium_driver, language)

        word_id = selenium_driver.find_element(By.ID, "wordId").get_attribute("value")
        tense = selenium_driver.find_element(By.ID, "tense").get_attribute("value")

        conjugation = Conjugation.objects.filter(word=word_id, tense=tense).first()
        feedback_message = self.input_answer(selenium_driver)

        assert feedback_message == 'Wrong answer\n' + \
               language.personal_pronoun_1 + " " + conjugation.conjugation_1 + "\n" + \
               language.personal_pronoun_2 + " " + conjugation.conjugation_2 + "\n" + \
               language.personal_pronoun_3 + " " + conjugation.conjugation_3 + "\n" + \
               language.personal_pronoun_4 + " " + conjugation.conjugation_4 + "\n" + \
               language.personal_pronoun_5 + " " + conjugation.conjugation_5 + "\n" + \
               language.personal_pronoun_6 + " " + conjugation.conjugation_6
        assert_menu(selenium_driver, False)

    @pytest.mark.django_db
    def test_conjugation_game_correct_answer_authenticated_user(self, live_server, selenium_driver,
                                                                conjugation_game_dependencies, account, score):
        user, password = account()[0]
        conjugation_game, words = conjugation_game_dependencies
        score(users=[user], games=[conjugation_game], languages=Language.objects.all())
        authenticate(live_server, selenium_driver, user.username, password)
        language = self.get_language_for_setup()

        initial_score = Score.objects.filter(user=user, game=conjugation_game, language=language).first().score

        self.select_language(live_server, selenium_driver, language)

        word_id = selenium_driver.find_element(By.ID, "wordId").get_attribute("value")
        tense = selenium_driver.find_element(By.ID, "tense").get_attribute("value")

        conjugation = Conjugation.objects.filter(word=word_id, tense=tense).first()
        answer = [conjugation.conjugation_1, conjugation.conjugation_2, conjugation.conjugation_3,
                  conjugation.conjugation_4, conjugation.conjugation_5, conjugation.conjugation_6]
        feedback_message = self.input_answer(selenium_driver, answer)

        final_score = Score.objects.filter(user=user, game=conjugation_game, language=language).first().score

        assert feedback_message == "Correct :)\n" + \
               language.personal_pronoun_1 + " " + conjugation.conjugation_1 + "\n" + \
               language.personal_pronoun_2 + " " + conjugation.conjugation_2 + "\n" + \
               language.personal_pronoun_3 + " " + conjugation.conjugation_3 + "\n" + \
               language.personal_pronoun_4 + " " + conjugation.conjugation_4 + "\n" + \
               language.personal_pronoun_5 + " " + conjugation.conjugation_5 + "\n" + \
               language.personal_pronoun_6 + " " + conjugation.conjugation_6 + "\n" + \
               "\nYour score is " + str(initial_score + 1)
        assert final_score == (initial_score + 1)
        assert_menu(selenium_driver, True)

    @pytest.mark.django_db
    def test_conjugation_game_wrong_answer_authenticated_user(self, live_server, selenium_driver,
                                                              conjugation_game_dependencies, account, score):
        user, password = account()[0]
        conjugation_game, words = conjugation_game_dependencies
        score(users=[user], games=[conjugation_game], languages=Language.objects.all())
        authenticate(live_server, selenium_driver, user.username, password)
        language = self.get_language_for_setup()

        initial_score = Score.objects.filter(user=user, game=conjugation_game, language=language).first().score

        self.select_language(live_server, selenium_driver, language)

        word_id = selenium_driver.find_element(By.ID, "wordId").get_attribute("value")
        tense = selenium_driver.find_element(By.ID, "tense").get_attribute("value")

        conjugation = Conjugation.objects.filter(word=word_id, tense=tense).first()
        feedback_message = self.input_answer(selenium_driver)

        final_score = Score.objects.filter(user=user, game=conjugation_game, language=language).first().score

        assert feedback_message == 'Wrong answer\n' + \
               language.personal_pronoun_1 + " " + conjugation.conjugation_1 + "\n" + \
               language.personal_pronoun_2 + " " + conjugation.conjugation_2 + "\n" + \
               language.personal_pronoun_3 + " " + conjugation.conjugation_3 + "\n" + \
               language.personal_pronoun_4 + " " + conjugation.conjugation_4 + "\n" + \
               language.personal_pronoun_5 + " " + conjugation.conjugation_5 + "\n" + \
               language.personal_pronoun_6 + " " + conjugation.conjugation_6
        assert final_score == initial_score
        assert_menu(selenium_driver, True)
