import random

from selenium.webdriver.common.by import By

from languageschool.models import Word
from languageschool.tests.selenium.utils import find_element, find_by_test_id, authenticate_user, \
    assert_meanings_of_word
from pajelingo.settings import FRONT_END_URL

CSS_SELECTOR_CARDS = (By.CSS_SELECTOR, "main .card")
CSS_SELECTOR_MEANING_CARD = (By.CSS_SELECTOR, "main .card .card-body .card-text")


def test_meaning_word_unauthenticated_user(live_server, selenium_driver, words, meanings):
    selenium_driver.get(f"{FRONT_END_URL}/dashboard")

    find_by_test_id(selenium_driver, "search-dropdown").click()
    find_by_test_id(selenium_driver, "dictionary-item").click()

    find_element(selenium_driver, CSS_SELECTOR_CARDS)
    cards = selenium_driver.find_elements(CSS_SELECTOR_CARDS[0], CSS_SELECTOR_CARDS[1])

    random_card = random.choice(cards)
    random_card.click()

    word_id = selenium_driver.current_url.split(FRONT_END_URL + "/meanings/")[1].split("#")[0]
    word = Word.objects.get(id=word_id)

    title = find_by_test_id(selenium_driver, "title")
    assert title.text == f"Meanings of \"{word.word_name}\""

    assert_meanings_of_word(selenium_driver, word)


def test_meaning_word_authenticated_user(live_server, selenium_driver, account, words, meanings):
    user, password = account()[0]

    authenticate_user(selenium_driver, user.username, password)

    selenium_driver.get(f"{FRONT_END_URL}/dashboard")

    find_by_test_id(selenium_driver, "search-dropdown").click()
    find_by_test_id(selenium_driver, "dictionary-item").click()

    find_element(selenium_driver, CSS_SELECTOR_CARDS)
    cards = selenium_driver.find_elements(CSS_SELECTOR_CARDS[0], CSS_SELECTOR_CARDS[1])

    random_card = random.choice(cards)
    random_card.click()

    word_id = selenium_driver.current_url.split(FRONT_END_URL + "/meanings/")[1].split("#")[0]
    word = Word.objects.get(id=word_id)

    title = find_by_test_id(selenium_driver, "title")
    assert title.text == f"Meanings of \"{word.word_name}\""

    assert_meanings_of_word(selenium_driver, word)

    heart_icon_button = find_by_test_id(selenium_driver, "favorite-button")

    if user.favorite_words.contains(word):
        assert heart_icon_button.text == "Remove from favorite words"
        find_element(selenium_driver, (By.CSS_SELECTOR, "main .btn-info .bi-heart"))
    else:
        assert heart_icon_button.text == "Add to favorite words"
        find_element(selenium_driver, (By.CSS_SELECTOR, "main .btn-info .bi-heart-fill"))