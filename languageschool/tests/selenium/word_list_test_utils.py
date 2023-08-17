import math
import random

from selenium.webdriver.common.by import By

from languageschool.models import Word, Meaning, User
from languageschool.tests.selenium.utils import find_element, wait_text_to_be_present, \
    wait_number_of_elements_to_be, scroll_to_element, assert_pagination, go_to_next_page, \
    CSS_SELECTOR_ACTIVE_PAGE_BUTTON, find_by_test_id
from pajelingo.settings import FRONT_END_URL

CSS_SELECTOR_FORM_CHECK = (By.CSS_SELECTOR, "body .modal .modal-body .form-check")
CSS_SELECTOR_CARDS = (By.CSS_SELECTOR, "main .card")
CSS_SELECTOR_HEART_NON_FILL_ICON = (By.CSS_SELECTOR, "main .card .bi-heart")
CSS_SELECTOR_HEART_FILL_ICON = (By.CSS_SELECTOR, "main .card .bi-heart-fill")
CSS_SELECTOR_MEANING_CARD = (By.CSS_SELECTOR, "main .card .card-body .card-text")

TEST_ID_FILTER_BUTTON = "filter-button"
TEST_ID_SEARCH_INPUT = "search-input"
TEST_ID_APPLY_FILTER_BUTTON = "apply-filters-button"
TEST_ID_NO_RESULTS = "no-results"
TEST_ID_NO_RESULTS_IMG = "no-results-img"


def get_card_language(card):
    flag_img = card.find_element(By.CSS_SELECTOR, "img")
    alt_flag_img = flag_img.get_attribute("alt")
    return alt_flag_img.split(" language flag")[0]


def get_card_word(card):
    return card.find_element(By.CSS_SELECTOR, ".card-body .card-text").text

def assert_search_results(selenium_driver, user=None, language=None, search_pattern=""):
    cards = selenium_driver.find_elements(CSS_SELECTOR_CARDS[0], CSS_SELECTOR_CARDS[1])

    for card in cards:
        language_name = get_card_language(card)
        word_name = get_card_word(card)

        word = Word.objects.filter(
            language__language_name=language_name,
            word_name=word_name
        ).first()

        assert word is not None

        if user is not None:
            is_heart_filled = user.favorite_words.contains(word)

            if is_heart_filled:
                find_element(selenium_driver, CSS_SELECTOR_HEART_FILL_ICON)
            else:
                find_element(selenium_driver, CSS_SELECTOR_HEART_NON_FILL_ICON)

        if language is not None:
            assert language_name == language.language_name

        assert search_pattern.lower() in word_name.lower()


def wait_toggle_heart_icon(random_card, expected_locator):
    counter = 0
    toggled_icons = random_card.find_elements(expected_locator[0], expected_locator[1])

    while (len(toggled_icons) == 0) and (counter < 100):
        toggled_icons = random_card.find_elements(expected_locator[0], expected_locator[1])
        counter += 1


def assert_meaning_page(selenium_driver, word_name, language_name, user=None):
    word_id = selenium_driver.current_url.split(FRONT_END_URL + "/meanings/")[1].split("#")[0]

    word = Word.objects.select_related("language").get(id=word_id)

    assert word.word_name == word_name
    assert word.language.language_name == language_name

    title = find_by_test_id(selenium_driver, "title")
    assert title.text == f"Meanings of \"{word.word_name}\""

    cards = selenium_driver.find_elements(CSS_SELECTOR_MEANING_CARD[0], CSS_SELECTOR_MEANING_CARD[1])

    nb_cards = len(cards)

    for i in range(nb_cards):
        card = cards[i]

        separator = "Meaning: " if (nb_cards == 1) else f"Meaning number {i + 1}: "
        meaning = card.text.split(separator)[1]

        assert Meaning.objects.filter(
            word=word,
            meaning=meaning
        ).exists()

    if user is not None:
        heart_icon_button = find_element(selenium_driver, (By.CSS_SELECTOR, "main .btn-info"))

        is_favorite_word = user.favorite_words.contains(word)

        assert heart_icon_button.text == "Remove from favorite words" if is_favorite_word else "Add to favorite words"

        if is_favorite_word:
            find_element(selenium_driver, (By.CSS_SELECTOR, "main .btn-info .bi-heart"))
        else:
            find_element(selenium_driver, (By.CSS_SELECTOR, "main .btn-info .bi-heart-fill"))


def search(selenium_driver, words, user):
    number_words = words.count()
    number_pages = math.ceil(number_words / 12)

    for i in range(number_pages):
        current_page = i + 1

        wait_text_to_be_present(selenium_driver, CSS_SELECTOR_ACTIVE_PAGE_BUTTON, str(current_page))

        assert_search_results(selenium_driver, user=user)
        assert_pagination(selenium_driver, current_page, number_pages)

        go_to_next_page(selenium_driver, current_page, number_pages)


def search_with_search_pattern_and_language_filter(selenium_driver, words, user, search_pattern, language):
    filter_button = find_by_test_id(selenium_driver, TEST_ID_FILTER_BUTTON)
    filter_button.click()

    search_form_input = find_by_test_id(selenium_driver, TEST_ID_SEARCH_INPUT).find_element(By.CSS_SELECTOR, "input")
    search_form_input.send_keys(search_pattern)

    find_element(selenium_driver, CSS_SELECTOR_FORM_CHECK)
    search_form_checkboxes = selenium_driver.find_elements(CSS_SELECTOR_FORM_CHECK[0], CSS_SELECTOR_FORM_CHECK[1])

    for search_form_checkbox in search_form_checkboxes:
        if search_form_checkbox.text != language.language_name:
            search_form_checkbox.find_element(By.CSS_SELECTOR, ".form-check-input").click()

    search_form_submit_button = find_by_test_id(selenium_driver, TEST_ID_APPLY_FILTER_BUTTON)
    search_form_submit_button.click()

    words = words.filter(word_name__icontains=search_pattern, language=language)
    number_words = words.count()
    number_pages = math.ceil(number_words / 12)

    for i in range(number_pages):
        current_page = i + 1

        wait_text_to_be_present(selenium_driver, CSS_SELECTOR_ACTIVE_PAGE_BUTTON, str(current_page))

        assert_search_results(selenium_driver, user=user, language=language, search_pattern=search_pattern)
        assert_pagination(selenium_driver, current_page, number_pages)

        go_to_next_page(selenium_driver, current_page, number_pages)


def toggle_favorite_word(selenium_driver, user):
    wait_text_to_be_present(selenium_driver, CSS_SELECTOR_ACTIVE_PAGE_BUTTON, "1")

    find_element(selenium_driver, CSS_SELECTOR_CARDS)
    cards = selenium_driver.find_elements(CSS_SELECTOR_CARDS[0], CSS_SELECTOR_CARDS[1])

    random_card = random.choice(cards)

    language_name = get_card_language(random_card)
    word_name = get_card_word(random_card)

    word = Word.objects.filter(
        language__language_name=language_name,
        word_name=word_name
    ).first()

    is_favorite_word = user.favorite_words.contains(word)

    if is_favorite_word:
        heart_fill_icon = random_card.find_element(CSS_SELECTOR_HEART_FILL_ICON[0], CSS_SELECTOR_HEART_FILL_ICON[1])
        heart_fill_icon.click()
        wait_toggle_heart_icon(random_card, CSS_SELECTOR_HEART_NON_FILL_ICON)
        assert not User.objects.get(id=user.id).favorite_words.contains(word)
    else:
        heart_non_fill_icon = \
            random_card.find_element(CSS_SELECTOR_HEART_NON_FILL_ICON[0], CSS_SELECTOR_HEART_NON_FILL_ICON[1])
        heart_non_fill_icon.click()
        wait_toggle_heart_icon(random_card, CSS_SELECTOR_HEART_FILL_ICON)
        assert User.objects.get(id=user.id).favorite_words.contains(word)

def search_with_no_results(selenium_driver):
    filter_button = find_by_test_id(selenium_driver, TEST_ID_FILTER_BUTTON)
    filter_button.click()

    find_element(selenium_driver, CSS_SELECTOR_FORM_CHECK)
    search_form_checkboxes = selenium_driver.find_elements(CSS_SELECTOR_FORM_CHECK[0], CSS_SELECTOR_FORM_CHECK[1])

    for search_form_checkbox in search_form_checkboxes:
        search_form_checkbox.find_element(By.CSS_SELECTOR, ".form-check-input").click()

    search_form_submit_button = find_by_test_id(selenium_driver, TEST_ID_APPLY_FILTER_BUTTON)
    search_form_submit_button.click()

    no_results = find_by_test_id(selenium_driver, TEST_ID_NO_RESULTS)
    no_results_img = find_by_test_id(selenium_driver, TEST_ID_NO_RESULTS_IMG)

    assert no_results.text == "No result matching your search was found"
    assert no_results_img.get_attribute("alt") == "No results"


def access_meaning_page(selenium_driver, user):
    filter_button = find_by_test_id(selenium_driver, TEST_ID_FILTER_BUTTON)
    filter_button.click()

    search_form_submit_button = find_by_test_id(selenium_driver, TEST_ID_APPLY_FILTER_BUTTON)
    search_form_submit_button.click()

    wait_text_to_be_present(selenium_driver, CSS_SELECTOR_ACTIVE_PAGE_BUTTON, "1")

    cards = selenium_driver.find_elements(CSS_SELECTOR_CARDS[0], CSS_SELECTOR_CARDS[1])

    random_card = random.choice(cards)

    language_name = get_card_language(random_card)
    word_name = get_card_word(random_card)

    random_card.click()

    assert_meaning_page(selenium_driver, word_name, language_name, user=user)


def toggle_favorite_word_in_meaning_page(selenium_driver, user):
    filter_button = find_by_test_id(selenium_driver, TEST_ID_FILTER_BUTTON)
    filter_button.click()

    search_form_submit_button = find_by_test_id(selenium_driver, TEST_ID_APPLY_FILTER_BUTTON)
    search_form_submit_button.click()

    wait_text_to_be_present(selenium_driver, CSS_SELECTOR_ACTIVE_PAGE_BUTTON, "1")

    cards = selenium_driver.find_elements(CSS_SELECTOR_CARDS[0], CSS_SELECTOR_CARDS[1])

    random_card = random.choice(cards)

    random_card.click()

    word_id = selenium_driver.current_url.split(FRONT_END_URL + "/meanings/")[1].split("#")[0]

    word = Word.objects.get(id=word_id)

    meanings = Meaning.objects.filter(word=word)

    wait_number_of_elements_to_be(selenium_driver, CSS_SELECTOR_MEANING_CARD, len(meanings))

    heart_icon_button = find_element(selenium_driver, (By.CSS_SELECTOR, "main .btn-info"))
    scroll_to_element(selenium_driver, heart_icon_button)

    is_favorite_word = user.favorite_words.contains(word)

    if is_favorite_word:
        find_element(selenium_driver, (By.CSS_SELECTOR, "main .btn-info .bi-heart"))
        heart_icon_button.click()
        find_element(selenium_driver, (By.CSS_SELECTOR, "main .btn-info .bi-heart-fill"))
        assert not User.objects.get(id=user.id).favorite_words.contains(word)
    else:
        find_element(selenium_driver, (By.CSS_SELECTOR, "main .btn-info .bi-heart-fill"))
        heart_icon_button.click()
        find_element(selenium_driver, (By.CSS_SELECTOR, "main .btn-info .bi-heart"))
        assert User.objects.get(id=user.id).favorite_words.contains(word)
