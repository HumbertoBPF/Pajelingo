import pytest
from selenium.webdriver.common.by import By

from languageschool.tests.selenium.utils import wait_number_of_elements_to_be
from pajelingo.settings import FRONT_END_URL

GAME_LIST_URL = FRONT_END_URL + "/games"
CSS_SELECTOR_GAME_CARDS = (By.CSS_SELECTOR, "main .card")


@pytest.mark.django_db
def test_game_list(live_server, selenium_driver, games):
    selenium_driver.get(GAME_LIST_URL)

    wait_number_of_elements_to_be(selenium_driver, CSS_SELECTOR_GAME_CARDS, 3)
    game_cards = selenium_driver.find_elements(CSS_SELECTOR_GAME_CARDS[0], CSS_SELECTOR_GAME_CARDS[1])

    for i in range(games.count()):
        card_text = game_cards[i].find_element(By.CSS_SELECTOR, ".card-text")
        assert card_text.text == games[i].game_name