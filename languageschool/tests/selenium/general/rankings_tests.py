import random

import pytest
from django.db.models import Sum
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

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
        if language is None:
            language = Language.objects.first()

        return Score.objects.filter(language=language).values('user__username')\
            .annotate(score=Sum('score')).order_by('-score')

    def wait_ranking_render(self, selenium_driver):
        # Wait the ranking table to be rendered
        WebDriverWait(selenium_driver, 10) \
            .until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, "main table thead tr th"), "Position"))

    def select_dropdown_item(self, selenium_driver, selected_item):
        # Wait the ranking table to be rendered
        self.wait_ranking_render(selenium_driver)
        selenium_driver.find_element(By.CSS_SELECTOR, "main .dropdown .dropdown-toggle").click()
        # Wait the dropdown items to be displayed
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "main .dropdown .dropdown-menu .dropdown-item")))
        dropdown_items \
            = selenium_driver.find_elements(By.CSS_SELECTOR, "main .dropdown .dropdown-menu .dropdown-item")
        # Click on the item corresponding to the selected language
        for dropdown_item in dropdown_items:
            if dropdown_item.text == selected_item:
                dropdown_item.click()
                break

    def assert_ranking(self, selenium_driver, language):
        scores = self.get_ranking(language)

        header = selenium_driver.find_element(By.CSS_SELECTOR, "h5")
        dropdown_button = selenium_driver.find_element(By.CSS_SELECTOR, "main .dropdown .dropdown-toggle")
        ths = selenium_driver.find_elements(By.CSS_SELECTOR, "main table thead tr th")
        tds = selenium_driver.find_elements(By.CSS_SELECTOR, "main table tbody tr td")

        assert header.text == "Rankings"
        assert dropdown_button.text == language.language_name

        assert ths[0].text == "Position"
        assert ths[1].text == "Username"
        assert ths[2].text == "Score"

        for i in range(len(scores)):
            assert tds[3 * i].text == str(i + 1)
            assert tds[3 * i + 1].text == str(scores[i].get("user__username"))
            assert tds[3 * i + 2].text == str(scores[i].get("score"))

    def assert_user_position_in_rankings(self, selenium_driver, user, language):
        scores = self.get_ranking(language)

        my_position = None
        my_score = None
        for i in range(len(scores)):
            if scores[i].get("user__username") == user.username:
                my_position = str(i + 1)
                my_score = str(scores[i].get("score"))

        separators = selenium_driver.find_elements(By.CSS_SELECTOR, "main table tbody tr td")
        ths = selenium_driver.find_elements(By.CSS_SELECTOR, "main table tbody tr th")

        assert separators[-1].text == "..."
        assert separators[-2].text == "..."
        assert separators[-3].text == "..."

        assert ths[0].text == "(You) {}".format(my_position)
        assert ths[1].text == user.username
        assert ths[2].text == my_score

    @pytest.mark.parametrize("has_language_filter", [True, False])
    @pytest.mark.django_db
    def test_game_filters(self, live_server, selenium_driver, account, score, games, languages, has_language_filter):
        """
        Checking that ranking is correctly rendered when no user is authenticated
        """
        self.prepare_test_scenario(live_server, selenium_driver, account, score)
        selected_language = random.choice(languages) if has_language_filter else Language.objects.first()

        url = live_server.url + reverse("rankings")
        selenium_driver.get(url)

        if has_language_filter:
            self.select_dropdown_item(selenium_driver, selected_language.language_name)

        self.wait_ranking_render(selenium_driver)

        self.assert_ranking(selenium_driver, selected_language)
        assert_menu(selenium_driver)

    @pytest.mark.parametrize("has_language_filter", [True, False])
    @pytest.mark.django_db
    def test_game_filters_with_authenticated_user(self, live_server, selenium_driver, account, score, games, languages,
                                                  has_language_filter):
        """
        Checking that the ranking is correctly rendered when users are authenticated
        """
        user, _ = self.prepare_test_scenario(live_server, selenium_driver, account, score, True)
        selected_language = random.choice(languages) if has_language_filter else Language.objects.first()

        url = live_server.url + reverse("rankings")
        selenium_driver.get(url)

        if has_language_filter:
            self.select_dropdown_item(selenium_driver, selected_language.language_name)

        self.wait_ranking_render(selenium_driver)

        self.assert_ranking(selenium_driver, selected_language)
        self.assert_user_position_in_rankings(selenium_driver, user, selected_language)

        assert_menu(selenium_driver, user=user)
