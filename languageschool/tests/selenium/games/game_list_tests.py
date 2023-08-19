import pytest

from languageschool.tests.selenium.utils import find_by_test_id
from pajelingo.settings import FRONT_END_URL

GAME_LIST_URL = f"{FRONT_END_URL}/games"


@pytest.mark.django_db
def test_game_list(live_server, selenium_driver, games):
    selenium_driver.get(GAME_LIST_URL)

    for game in games:
        game_card = find_by_test_id(selenium_driver, f"{game.id}-game-card")
        assert game_card.text == game.game_name