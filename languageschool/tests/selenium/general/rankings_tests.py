import math
import random

import pytest
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from languageschool.models import Game, Language
from languageschool.tests.selenium.utils import assert_menu, authenticate
from languageschool.tests.utils import get_ranking, scroll_to_element


class TestsRankingsSelenium:
    def prepare_test_scenario(self, live_server, selenium_driver, account_fixture, score_fixture, nb_users, auth=False):
        accounts = account_fixture(n=nb_users)

        users = []

        for account in accounts:
            users.append(account[0])

        score_fixture(users=users, games=Game.objects.all(), languages=Language.objects.all())

        if auth:
            user, password = random.choice(accounts)
            authenticate(live_server, selenium_driver, user.username, password)
            return user

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

    def assert_ranking_headers(self, selenium_driver, language):
        header = selenium_driver.find_element(By.CSS_SELECTOR, "h5")
        dropdown_button = selenium_driver.find_element(By.CSS_SELECTOR, "main .dropdown .dropdown-toggle")
        ths = selenium_driver.find_elements(By.CSS_SELECTOR, "main table thead tr th")

        assert header.text == "Rankings"
        assert dropdown_button.text == language.language_name
        assert ths[0].text == "Position"
        assert ths[1].text == "Username"
        assert ths[2].text == "Score"

    def assert_user_position_in_rankings(self, selenium_driver, user, language):
        scores = get_ranking(language)

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

    def get_displayed_scores(self, selenium_driver):
        rendered_scores = []
        ranking_rows = selenium_driver.find_elements(By.CSS_SELECTOR, "main table tbody tr")
        number_of_rows = len(ranking_rows)
        # Add the displayed rows
        for i in range(number_of_rows):
            tds = ranking_rows[i].find_elements(By.CSS_SELECTOR, "td")
            # Stop in the line right before the user's position
            if (tds[0].text == "...") and (tds[1].text == "...") and (tds[2].text == "..."):
                break
            rendered_scores.append([tds[0].text, tds[1].text, tds[2].text])

        return rendered_scores

    def assert_scores_in_all_pages(self, selenium_driver, language, increasing, authenticated_user=None):
        expected_scores = get_ranking(language)
        nb_pages = math.ceil(len(expected_scores) / 10)

        css_selector = ".pagination .page-item [data-{}-button]".format("next" if increasing else "previous")

        self.wait_ranking_render(selenium_driver)
        nav_buttons = selenium_driver.find_elements(By.CSS_SELECTOR, css_selector)

        rendered_scores = []
        current_page = 1 if increasing else nb_pages

        while len(nav_buttons) > 0:
            self.wait_ranking_render(selenium_driver)

            ranking_rows = self.get_displayed_scores(selenium_driver)
            rendered_scores = (rendered_scores + ranking_rows) if increasing else (ranking_rows + rendered_scores)
            # Check ranking headers
            self.assert_ranking_headers(selenium_driver, language)
            # Checking active page
            active_page = selenium_driver.find_element(By.CSS_SELECTOR, ".pagination .active .page-link")
            assert active_page.text == str(current_page)
            # If there is a user authenticated, check the position of this user in the ranking
            if authenticated_user is not None:
                self.assert_user_position_in_rankings(selenium_driver, authenticated_user, language)
            # Go to next page
            nav_buttons = selenium_driver.find_elements(By.CSS_SELECTOR, css_selector)
            if len(nav_buttons) > 0:
                current_page += 1 if increasing else -1
                scroll_to_element(selenium_driver, nav_buttons[0])
                nav_buttons[0].click()

        self.assert_scores(rendered_scores, expected_scores)

    def assert_scores(self, rendered_scores, expected_scores):
        number_expected_scores = len(expected_scores)
        assert len(rendered_scores) == number_expected_scores

        for i in range(number_expected_scores):
            assert rendered_scores[i][0] == str(expected_scores[i].get("position"))
            assert rendered_scores[i][1] == expected_scores[i].get("user__username")
            assert rendered_scores[i][2] == str(expected_scores[i].get("score"))

    def go_to_last_page(self, selenium_driver):
        last_page_button = selenium_driver \
            .find_elements(By.CSS_SELECTOR, ".pagination .page-item [data-page-button]")[-1]
        scroll_to_element(selenium_driver, last_page_button)
        last_page_button.click()
        self.wait_ranking_render(selenium_driver)

    def go_to_first_page(self, selenium_driver):
        first_page_button = selenium_driver \
            .find_elements(By.CSS_SELECTOR, ".pagination .page-item [data-page-button]")[0]
        scroll_to_element(selenium_driver, first_page_button)
        first_page_button.click()
        self.wait_ranking_render(selenium_driver)

    @pytest.mark.parametrize("is_authenticated", [True, False])
    @pytest.mark.django_db
    def test_rankings_no_filters(self, live_server, selenium_driver, account, score, games, languages,
                                 is_authenticated):
        """
        Checking that the ranking is correctly rendered according to the language filter applied.
        """
        user = self.prepare_test_scenario(live_server, selenium_driver, account, score, random.randint(5, 10),
                                          auth=is_authenticated)
        default_language = Language.objects.first()

        url = live_server.url + reverse("rankings")
        selenium_driver.get(url)

        self.wait_ranking_render(selenium_driver)

        self.assert_ranking_headers(selenium_driver, default_language)
        rendered_scores = self.get_displayed_scores(selenium_driver)
        scores = get_ranking(default_language)
        self.assert_scores(rendered_scores, scores)

        if is_authenticated:
            self.assert_user_position_in_rankings(selenium_driver, user, default_language)

        assert_menu(selenium_driver, user=user)

    @pytest.mark.parametrize("is_authenticated", [True, False])
    @pytest.mark.django_db
    def test_rankings_pagination_increasing_order(self, live_server, selenium_driver, account, score, games, languages,
                                                  is_authenticated):
        user = self.prepare_test_scenario(live_server, selenium_driver, account, score, random.randint(20, 50),
                                   auth=is_authenticated)

        random_language = random.choice(languages)

        url = live_server.url + reverse("rankings")
        selenium_driver.get(url)

        self.select_dropdown_item(selenium_driver, random_language.language_name)

        self.assert_scores_in_all_pages(selenium_driver, random_language, True, authenticated_user=user)

    @pytest.mark.parametrize("is_authenticated", [True, False])
    @pytest.mark.django_db
    def test_rankings_pagination_decreasing_order(self, live_server, selenium_driver, account, score, games, languages,
                                                  is_authenticated):
        user = self.prepare_test_scenario(live_server, selenium_driver, account, score, random.randint(20, 50),
                                   auth=is_authenticated)

        random_language = random.choice(languages)

        url = live_server.url + reverse("rankings")
        selenium_driver.get(url)

        self.select_dropdown_item(selenium_driver, random_language.language_name)
        self.wait_ranking_render(selenium_driver)
        last_page_button = selenium_driver.\
            find_elements(By.CSS_SELECTOR, ".pagination .page-item [data-page-button]")[-1]
        scroll_to_element(selenium_driver, last_page_button)
        last_page_button.click()

        self.assert_scores_in_all_pages(selenium_driver, random_language, False, authenticated_user=user)

    @pytest.mark.parametrize("is_authenticated", [True, False])
    @pytest.mark.django_db
    def test_redirect_to_last_page(self, live_server, selenium_driver, account, score, games, languages,
                                   is_authenticated):
        user = self.prepare_test_scenario(live_server, selenium_driver, account, score, random.randint(20, 50),
                                   auth=is_authenticated)

        random_language = random.choice(languages)
        expected_scores = get_ranking(random_language)

        url = live_server.url + reverse("rankings")
        selenium_driver.get(url)

        number_pages = math.ceil(len(expected_scores)/10)

        self.select_dropdown_item(selenium_driver, random_language.language_name)
        self.wait_ranking_render(selenium_driver)
        # Click on the last page button
        self.go_to_last_page(selenium_driver)
        # Check ranking headers
        self.assert_ranking_headers(selenium_driver, random_language)
        # Checking active page
        active_page = selenium_driver.find_element(By.CSS_SELECTOR, ".pagination .active .page-link")
        assert active_page.text == str(number_pages)
        # Checking the displayed scores
        rendered_scores = self.get_displayed_scores(selenium_driver)
        number_scores = len(expected_scores)
        number_scores_last_page = 10 if (number_scores % 10 == 0) else (number_scores % 10)
        self.assert_scores(rendered_scores, expected_scores[(number_scores-number_scores_last_page):])
        # If there is a user authenticated, check the position of this user in the ranking
        if user is not None:
            self.assert_user_position_in_rankings(selenium_driver, user, random_language)


    @pytest.mark.parametrize("is_authenticated", [True, False])
    @pytest.mark.django_db
    def test_redirect_to_first_page(self, live_server, selenium_driver, account, score, games, languages,
                                    is_authenticated):
        user = self.prepare_test_scenario(live_server, selenium_driver, account, score, random.randint(20, 50),
                                   auth=is_authenticated)

        random_language = random.choice(languages)
        expected_scores = get_ranking(random_language)

        url = live_server.url + reverse("rankings")
        selenium_driver.get(url)

        number_pages = math.ceil(len(expected_scores) / 10)

        self.select_dropdown_item(selenium_driver, random_language.language_name)
        self.wait_ranking_render(selenium_driver)
        # Click on the last page button
        self.go_to_last_page(selenium_driver)
        # Click on the first page button
        self.go_to_first_page(selenium_driver)
        # Check ranking headers
        self.assert_ranking_headers(selenium_driver, random_language)
        # Checking active page
        active_page = selenium_driver.find_element(By.CSS_SELECTOR, ".pagination .active .page-link")
        assert active_page.text == "1"
        # Checking the displayed scores
        rendered_scores = self.get_displayed_scores(selenium_driver)
        self.assert_scores(rendered_scores, expected_scores[:10])
        # If there is a user authenticated, check the position of this user in the ranking
        if user is not None:
            self.assert_user_position_in_rankings(selenium_driver, user, random_language)
