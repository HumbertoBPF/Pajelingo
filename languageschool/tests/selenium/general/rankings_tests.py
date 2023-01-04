import random
from urllib.parse import urlencode

import pytest
from django.db.models import Sum
from django.urls import reverse
from selenium.webdriver.common.by import By

from languageschool.models import Score, Game, Language
from languageschool.tests.selenium.utils import assert_menu, authenticate


class TestsRankingsSelenium:
    def prepare_test_scenario(self, live_server, selenium_driver, account_fixture, score_fixture, auth=False):
        accounts = account_fixture(n=random.randint(5, 10))

        users = []

        for account in accounts:
            users.append(account[0])

        score_fixture(users=users, games=Game.objects.all(), languages=Language.objects.all())

        if auth:
            user, password = random.choice(accounts)
            authenticate(live_server, selenium_driver, user.username, password)
            return user, password

    def get_ranking(self, language):
        scores = Score.objects.all()

        if language is not None:
            scores = scores.filter(language__language_name=language.language_name)

        return scores.values('user__username').annotate(score=Sum('score')).order_by('-score')

    def assert_ranking(self, live_server, selenium_driver, language):
        scores = self.get_ranking(language)[:10]

        url = live_server.url + reverse("rankings")
        if language is not None:
            query_string = urlencode({'language': language.language_name})
            url = '{}?{}'.format(url, query_string)

        selenium_driver.get(url)

        header = selenium_driver.find_element(By.TAG_NAME, "h5")
        ths = selenium_driver.find_elements(By.TAG_NAME, "th")
        tds = selenium_driver.find_element(By.CLASS_NAME, "table").find_elements(By.TAG_NAME, "td")

        assert header.text == "General ranking" if language is None else (language.language_name + " ranking")

        assert ths[0].text == "Position"
        assert ths[1].text == "Username"
        assert ths[2].text == "Score"

        for i in range(len(scores)):
            assert tds[3 * i].text == str(i + 1)
            assert tds[3 * i + 1].text == str(scores[i].get("user__username"))
            assert tds[3 * i + 2].text == str(scores[i].get("score"))

    @pytest.mark.parametrize(
        "has_language_filter", [True, False]
    )
    @pytest.mark.django_db
    def test_game_filters(self, live_server, selenium_driver, account, score, games, languages, has_language_filter):
        """
        Checking that ranking is correctly rendered when no user is authenticated
        """
        self.prepare_test_scenario(live_server, selenium_driver, account, score)
        language = random.choice(languages) if has_language_filter else None
        self.assert_ranking(live_server, selenium_driver, language)
        assert_menu(selenium_driver)

    @pytest.mark.parametrize(
        "has_language_filter", [True, False]
    )
    @pytest.mark.django_db
    def test_game_filters_with_authenticated_user(self, live_server, selenium_driver, account, score, games, languages, has_language_filter):
        """
        Checking that the ranking is correctly rendered when users are authenticated
        """
        user, _ = self.prepare_test_scenario(live_server, selenium_driver, account, score, True)
        language = random.choice(languages) if has_language_filter else None

        self.assert_ranking(live_server, selenium_driver, language)

        scores = self.get_ranking(language)

        my_position = None
        my_score = None
        for i in range(len(scores)):
            if scores[i].get("user__username") == user.username:
                my_position = str(i + 1)
                my_score = str(scores[i].get("score"))

        separators = selenium_driver.find_element(By.ID, "separator").find_elements(By.TAG_NAME, "td")
        ths = selenium_driver.find_element(By.ID, "my_position").find_elements(By.TAG_NAME, "th")

        for i in range(3):
            assert separators[i].text == "..."

        assert ths[0].text == "(You) {}".format(my_position)
        assert ths[1].text == user.username
        assert ths[2].text == my_score
        assert_menu(selenium_driver, user=user)
