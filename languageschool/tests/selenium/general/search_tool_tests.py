import random
import time

import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By

from languageschool.models import Word, Meaning, Language
from languageschool.tests.selenium.utils import assert_menu


class TestSearchSelenium:
    def fill_search_form(self, live_server, selenium_driver, search_pattern, languages):
        url = live_server.url + reverse("search")
        selenium_driver.get(url)

        selenium_driver.find_element(By.ID, "searchInput").send_keys(search_pattern)

        for language in languages:
            selenium_driver.find_element(By.ID, "checkbox" + language.language_name).click()

        selenium_driver.find_element(By.ID, "searchSubmitButton").click()

    @pytest.mark.django_db
    def test_rendering_search_form(self, live_server, selenium_driver, words):
        url = live_server.url + reverse("search")
        selenium_driver.get(url)

        search_inputs = selenium_driver.find_elements(By.ID, "searchInput")

        for language in Language.objects.all():
            checkbox_languages = selenium_driver.find_elements(By.ID, "checkbox{}".format(language.language_name))
            assert len(checkbox_languages) == 1

        search_buttons = selenium_driver.find_elements(By.ID, "searchSubmitButton")

        assert len(search_inputs) == 1
        assert len(search_buttons) == 1
        assert_menu(selenium_driver)

    @pytest.mark.django_db
    def test_search_no_results(self, live_server, selenium_driver, words):
        self.fill_search_form(live_server, selenium_driver, "", [])

        no_result_imgs = selenium_driver.find_elements(By.ID, "noResultImg")
        no_result_ps = selenium_driver.find_elements(By.ID, "noResultP")

        assert len(no_result_imgs) == 1
        assert len(no_result_ps) == 1
        assert no_result_ps[0].text == "No result matching your search was found"
        assert_menu(selenium_driver)

    @pytest.mark.parametrize(
        "search_pattern", [
            "",
            get_random_string(1),
            get_random_string(random.randint(1, 5))
        ]
    )
    @pytest.mark.parametrize("all_languages", [True, False])
    @pytest.mark.django_db
    def test_search(self, live_server, selenium_driver, words, search_pattern, all_languages):
        number_languages = Language.objects.count()
        k = number_languages if all_languages else random.randint(1, number_languages)
        languages = random.sample(list(Language.objects.all()), k)

        self.fill_search_form(live_server, selenium_driver, search_pattern, languages)

        url = selenium_driver.current_url

        page_hrefs = set()
        page_hrefs.add(url)
        dict_words = {}

        words = words.filter(word_name__icontains=search_pattern, language__in=languages)

        pages = selenium_driver.find_elements(By.CLASS_NAME, "page-link")
        n = len(pages)
        for i in range(n):
            if i != 0:
                page = pages[i]
                page_hrefs.add(page.get_attribute("href"))

        for page in page_hrefs:
            selenium_driver.get(page)
            results_page = selenium_driver.find_elements(By.CLASS_NAME, "card-body")
            results_title = selenium_driver.find_elements(By.CLASS_NAME, "card-title")
            results_text = selenium_driver.find_elements(By.CLASS_NAME, "card-text")
            results_link = selenium_driver.find_elements(By.CLASS_NAME, "text-decoration-none")[:-2]
            n = len(results_page)
            for i in range(n):
                word_name = results_title[i].text
                language_name = results_text[i].text
                word_id = results_link[i].get_attribute("href").split("/meaning/")[1]
                word = words.filter(id=word_id, word_name=word_name, language__language_name=language_name).first()
                # Check if all the words that are expected to appear occur only once
                assert dict_words.get(word.id) is None
                dict_words[word.id] = True
                # Check if the word really contains the search pattern
                assert search_pattern.lower() in word_name.lower()

        assert len(dict_words) == len(words)
        assert_menu(selenium_driver)

    @pytest.mark.django_db
    def test_dictionary_access_with_click(self, live_server, selenium_driver, words, meanings):
        self.fill_search_form(live_server, selenium_driver, "", Language.objects.all())
        # Exclude the two last items because they correspond to the social network links
        results_page = selenium_driver.find_elements(By.CLASS_NAME, "text-decoration-none")[:-2]
        result_page = random.choice(results_page)
        word_id = result_page.get_attribute("href").split("/meaning/")[1]

        selenium_driver.execute_script("arguments[0].click();", result_page)

        word = Word.objects.get(pk=word_id)
        meanings = Meaning.objects.filter(word=word.id)
        meanings_dict = {}
        # Time necessary to all the elements be attached to the DOM
        time.sleep(1)

        card_titles = selenium_driver.find_elements(By.CLASS_NAME, "card-title")
        card_texts = selenium_driver.find_elements(By.CLASS_NAME, "card-text")
        n = len(card_texts)

        for i in range(n):
            title = card_titles[i].text
            text = card_texts[i].text[9:]
            # Verifying title of the meaning card
            assert title == str(word)
            # Verifying the meaning itself
            meaning = Meaning.objects.filter(word=word.id, meaning=text).first()
            assert meanings_dict.get(meaning.id) is None
            meanings_dict[meaning.id] = True
        # Verifying that all the expected meanings were displayed
        assert len(meanings) == len(meanings_dict)
        assert_menu(selenium_driver)
