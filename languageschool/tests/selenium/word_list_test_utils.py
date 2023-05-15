import math
import random
import time

from selenium.webdriver.common.by import By

from languageschool.models import Word, AppUser, Meaning
from languageschool.tests.selenium.utils import assert_menu, find_element, wait_text_to_be_present, \
    wait_number_of_elements_to_be, scroll_to_element, assert_pagination, go_to_next_page, \
    CSS_SELECTOR_ACTIVE_PAGE_BUTTON
from pajelingo.settings import FRONT_END_URL

SEARCH_URL = FRONT_END_URL + "/search"
CSS_SELECTOR_FILTER_BUTTON = (By.CSS_SELECTOR, "main .btn-info")
CSS_SELECTOR_SEARCH_FORM_INPUT = (By.CSS_SELECTOR, "body .modal .modal-body .form-floating .form-control")
CSS_SELECTOR_FORM_CHECK = (By.CSS_SELECTOR, "body .modal .modal-body .form-check")
CSS_SELECTOR_SUBMIT_BUTTON = (By.CSS_SELECTOR, "body .modal .modal-footer .btn-success")
CSS_SELECTOR_CARDS = (By.CSS_SELECTOR, "main .card")
CSS_SELECTOR_HEART_NON_FILL_ICON = (By.CSS_SELECTOR, "main .card .bi-heart")
CSS_SELECTOR_HEART_FILL_ICON = (By.CSS_SELECTOR, "main .card .bi-heart-fill")
CSS_SELECTOR_NO_RESULTS_IMG = (By.CSS_SELECTOR, "main img")
CSS_SELECTOR_NO_RESULTS_TEXT = (By.CSS_SELECTOR, "main p")
CSS_SELECTOR_MEANING_CARD = (By.CSS_SELECTOR, "main .card .card-body .card-text")


def get_card_language(card):
    flag_img = card.find_element(By.CSS_SELECTOR, "img")
    alt_flag_img = flag_img.get_attribute("alt")
    return alt_flag_img.split(" language flag")[0]


def get_card_word(card):
    return card.find_element(By.CSS_SELECTOR, ".card-body .card-text").text

def assert_search_results(selenium_driver, words, current_page, number_pages, app_user=None, language=None,
                          search_pattern=""):
    expected_number_of_cards = (len(words) % 12 if ((current_page == number_pages) and (len(words) % 12 != 0)) else 12)

    wait_number_of_elements_to_be(selenium_driver, CSS_SELECTOR_CARDS, expected_number_of_cards)
    cards = selenium_driver.find_elements(CSS_SELECTOR_CARDS[0], CSS_SELECTOR_CARDS[1])

    for card in cards:
        language_name = get_card_language(card)
        word_name = get_card_word(card)

        word = Word.objects.filter(
            language__language_name=language_name,
            word_name=word_name
        ).first()

        assert word is not None

        if app_user is not None:
            is_heart_filled = word in app_user.favorite_words.all()

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


def assert_meaning_page(selenium_driver, word_name, language_name, app_user=None):
    word_id = selenium_driver.current_url.split(FRONT_END_URL + "/meanings/")[1].split("#")[0]

    word = Word.objects.filter(
        id=word_id,
        word_name=word_name,
        language__language_name=language_name
    ).first()

    assert word is not None

    wait_text_to_be_present(selenium_driver, (By.CSS_SELECTOR, "main h5"), "Meanings of \"{}\"".format(word.word_name))
    title = find_element(selenium_driver, (By.CSS_SELECTOR, "main h5"))
    meanings = Meaning.objects.filter(word=word)

    meanings_dict = {}

    for meaning in meanings:
        meanings_dict[meaning.id] = True

    cards = selenium_driver.find_elements(CSS_SELECTOR_MEANING_CARD[0], CSS_SELECTOR_MEANING_CARD[1])

    assert title.text == "Meanings of \"{}\"".format(word.word_name)

    nb_cards = len(cards)

    for i in range(len(cards)):
        card = cards[i]

        separator = "Meaning: " if (nb_cards == 1) else "Meaning number {}: ".format(i + 1)
        meaning = card.text.split(separator)[1]

        meaning = Meaning.objects.filter(
            word=word,
            meaning=meaning
        ).first()

        del meanings_dict[meaning.id]

    assert len(meanings_dict) == 0

    if app_user is not None:
        heart_icon_button = find_element(selenium_driver, (By.CSS_SELECTOR, "main .btn-info"))

        is_favorite_word = word in app_user.favorite_words.all()

        assert heart_icon_button.text == "Remove from favorite words" if is_favorite_word else "Add to favorite words"

        if is_favorite_word:
            find_element(selenium_driver, (By.CSS_SELECTOR, "main .btn-info .bi-heart"))
        else:
            find_element(selenium_driver, (By.CSS_SELECTOR, "main .btn-info .bi-heart-fill"))


def modal_form_rendering(selenium_driver, languages, user):
    assert_menu(selenium_driver, user=user)

    filter_button = find_element(selenium_driver, CSS_SELECTOR_FILTER_BUTTON)
    filter_button.click()

    search_form_input = find_element(selenium_driver, CSS_SELECTOR_SEARCH_FORM_INPUT)
    find_element(selenium_driver, CSS_SELECTOR_FORM_CHECK)
    search_form_checkboxes = selenium_driver.find_elements(CSS_SELECTOR_FORM_CHECK[0], CSS_SELECTOR_FORM_CHECK[1])
    search_form_submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    assert search_form_input.get_attribute("placeholder") == "Search for..."
    assert len(search_form_checkboxes) == len(languages)

    for i in range(len(languages)):
        assert search_form_checkboxes[i].find_element(By.CSS_SELECTOR, "label").text == languages[i].language_name
        assert search_form_checkboxes[i].find_element(By.CSS_SELECTOR, "input") \
                   .get_attribute("value") == languages[i].language_name

    assert search_form_submit_button.text == "Apply"


def search(selenium_driver, words, app_user):
    number_pages = math.ceil(len(words) / 12)

    for i in range(number_pages):
        current_page = i + 1

        wait_text_to_be_present(selenium_driver, CSS_SELECTOR_ACTIVE_PAGE_BUTTON, str(current_page))

        assert_search_results(selenium_driver, words, current_page, number_pages, app_user=app_user)
        assert_pagination(selenium_driver, current_page, number_pages)

        go_to_next_page(selenium_driver, current_page, number_pages)


def search_with_language_filter(selenium_driver, words, app_user, language):
    filter_button = find_element(selenium_driver, CSS_SELECTOR_FILTER_BUTTON)
    filter_button.click()

    find_element(selenium_driver, CSS_SELECTOR_FORM_CHECK)
    search_form_checkboxes = selenium_driver.find_elements(CSS_SELECTOR_FORM_CHECK[0], CSS_SELECTOR_FORM_CHECK[1])
    search_form_submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    for search_form_checkbox in search_form_checkboxes:
        if search_form_checkbox.text != language.language_name:
            search_form_checkbox.find_element(By.CSS_SELECTOR, ".form-check-input").click()

    search_form_submit_button.click()

    words = words.filter(language=language)
    number_pages = math.ceil(len(words) / 12)

    for i in range(number_pages):
        current_page = i + 1

        wait_text_to_be_present(selenium_driver, CSS_SELECTOR_ACTIVE_PAGE_BUTTON, str(current_page))

        assert_search_results(selenium_driver, words, current_page, number_pages, app_user=app_user,
                              language=language)
        assert_pagination(selenium_driver, current_page, number_pages)

        go_to_next_page(selenium_driver, current_page, number_pages)


def search_with_search_pattern(selenium_driver, words, app_user, search_pattern):
    time.sleep(1)
    filter_button = find_element(selenium_driver, CSS_SELECTOR_FILTER_BUTTON)
    filter_button.click()

    search_form_input = find_element(selenium_driver, CSS_SELECTOR_SEARCH_FORM_INPUT)
    search_form_submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    search_form_input.send_keys(search_pattern)
    search_form_submit_button.click()

    words = words.filter(word_name__icontains=search_pattern)
    number_pages = math.ceil(len(words) / 12)

    for i in range(number_pages):
        current_page = i + 1

        wait_text_to_be_present(selenium_driver, CSS_SELECTOR_ACTIVE_PAGE_BUTTON, str(current_page))
        assert_search_results(selenium_driver, words, current_page, number_pages, app_user=app_user,
                              search_pattern=search_pattern)
        assert_pagination(selenium_driver, current_page, number_pages)

        go_to_next_page(selenium_driver, current_page, number_pages)


def search_with_search_pattern_and_language_filter(selenium_driver, words, app_user, search_pattern, language):
    filter_button = find_element(selenium_driver, CSS_SELECTOR_FILTER_BUTTON)
    filter_button.click()

    search_form_input = find_element(selenium_driver, CSS_SELECTOR_SEARCH_FORM_INPUT)
    find_element(selenium_driver, CSS_SELECTOR_FORM_CHECK)
    search_form_checkboxes = selenium_driver.find_elements(CSS_SELECTOR_FORM_CHECK[0], CSS_SELECTOR_FORM_CHECK[1])
    search_form_submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    search_form_input.send_keys(search_pattern)
    for search_form_checkbox in search_form_checkboxes:
        if search_form_checkbox.text != language.language_name:
            search_form_checkbox.find_element(By.CSS_SELECTOR, ".form-check-input").click()

    search_form_submit_button.click()

    words = words.filter(word_name__icontains=search_pattern, language=language)
    number_pages = math.ceil(len(words) / 12)

    for i in range(number_pages):
        current_page = i + 1

        wait_text_to_be_present(selenium_driver, CSS_SELECTOR_ACTIVE_PAGE_BUTTON, str(current_page))

        assert_search_results(selenium_driver, words, current_page, number_pages, app_user=app_user, language=language,
                              search_pattern=search_pattern)
        assert_pagination(selenium_driver, current_page, number_pages)

        go_to_next_page(selenium_driver, current_page, number_pages)


def toggle_favorite_word(selenium_driver, app_user):
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

    is_favorite_word = word in app_user.favorite_words.all()

    if is_favorite_word:
        heart_fill_icon = random_card.find_element(CSS_SELECTOR_HEART_FILL_ICON[0], CSS_SELECTOR_HEART_FILL_ICON[1])
        heart_fill_icon.click()
        wait_toggle_heart_icon(random_card, CSS_SELECTOR_HEART_NON_FILL_ICON)
        assert not word in AppUser.objects.get(id=app_user.id).favorite_words.all()
    else:
        heart_non_fill_icon = \
            random_card.find_element(CSS_SELECTOR_HEART_NON_FILL_ICON[0], CSS_SELECTOR_HEART_NON_FILL_ICON[1])
        heart_non_fill_icon.click()
        wait_toggle_heart_icon(random_card, CSS_SELECTOR_HEART_FILL_ICON)
        assert word in AppUser.objects.get(id=app_user.id).favorite_words.all()

def search_with_no_results(selenium_driver):
    filter_button = find_element(selenium_driver, CSS_SELECTOR_FILTER_BUTTON)
    filter_button.click()

    find_element(selenium_driver, CSS_SELECTOR_FORM_CHECK)
    search_form_checkboxes = selenium_driver.find_elements(CSS_SELECTOR_FORM_CHECK[0], CSS_SELECTOR_FORM_CHECK[1])
    search_form_submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    for search_form_checkbox in search_form_checkboxes:
        search_form_checkbox.find_element(By.CSS_SELECTOR, ".form-check-input").click()

    search_form_submit_button.click()

    no_results_img = find_element(selenium_driver, CSS_SELECTOR_NO_RESULTS_IMG)
    no_results_text = find_element(selenium_driver, CSS_SELECTOR_NO_RESULTS_TEXT)

    assert no_results_img.get_attribute("alt") == "No results"
    assert no_results_text.text == "No result matching your search was found"


def access_meaning_page(selenium_driver, app_user):
    filter_button = find_element(selenium_driver, CSS_SELECTOR_FILTER_BUTTON)
    filter_button.click()

    search_form_submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    search_form_submit_button.click()

    wait_text_to_be_present(selenium_driver, CSS_SELECTOR_ACTIVE_PAGE_BUTTON, "1")

    cards = selenium_driver.find_elements(CSS_SELECTOR_CARDS[0], CSS_SELECTOR_CARDS[1])

    random_card = random.choice(cards)

    language_name = get_card_language(random_card)
    word_name = get_card_word(random_card)

    random_card.click()

    assert_meaning_page(selenium_driver, word_name, language_name, app_user=app_user)


def toggle_favorite_word_in_meaning_page(selenium_driver, app_user):
    filter_button = find_element(selenium_driver, CSS_SELECTOR_FILTER_BUTTON)
    filter_button.click()

    search_form_submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)
    search_form_submit_button.click()

    wait_text_to_be_present(selenium_driver, CSS_SELECTOR_ACTIVE_PAGE_BUTTON, "1")

    cards = selenium_driver.find_elements(CSS_SELECTOR_CARDS[0], CSS_SELECTOR_CARDS[1])

    random_card = random.choice(cards)

    language_name = get_card_language(random_card)
    word_name = get_card_word(random_card)

    random_card.click()

    word_id = selenium_driver.current_url.split(FRONT_END_URL + "/meanings/")[1].split("#")[0]

    word = Word.objects.filter(
        id=word_id,
        word_name=word_name,
        language__language_name=language_name
    ).first()
    meanings = Meaning.objects.filter(word=word)

    wait_number_of_elements_to_be(selenium_driver, CSS_SELECTOR_MEANING_CARD, len(meanings))

    heart_icon_button = find_element(selenium_driver, (By.CSS_SELECTOR, "main .btn-info"))
    scroll_to_element(selenium_driver, heart_icon_button)

    is_favorite_word = word in app_user.favorite_words.all()

    if is_favorite_word:
        find_element(selenium_driver, (By.CSS_SELECTOR, "main .btn-info .bi-heart"))
        heart_icon_button.click()
        find_element(selenium_driver, (By.CSS_SELECTOR, "main .btn-info .bi-heart-fill"))
        assert not word in AppUser.objects.get(id=app_user.id).favorite_words.all()
    else:
        find_element(selenium_driver, (By.CSS_SELECTOR, "main .btn-info .bi-heart-fill"))
        heart_icon_button.click()
        find_element(selenium_driver, (By.CSS_SELECTOR, "main .btn-info .bi-heart"))
        assert word in AppUser.objects.get(id=app_user.id).favorite_words.all()
