import pytest
from django.urls import reverse
from selenium.webdriver.common.by import By


class TestSearchSelenium:
    @pytest.mark.django_db
    def test_rendering_about_us_page(self, live_server, selenium_driver):
        url = live_server.url + reverse("about-us")
        selenium_driver.get(url)

        image_names = [
            "images/about_us/onboarding_0.png",
            "images/about_us/onboarding_1.png",
            "images/about_us/onboarding_2.png",
            "images/about_us/onboarding_3.png",
            "images/about_us/onboarding_4.png"
        ]
        captions = [
            "Welcome to Pajelingo!",
            "Here you find help to learn foreign languages :)",
            "Use the search tool to expand your vocabulary! In order to keep your imersion in your target "
            "language, we provide meanings instead of translations :)",
            "We have several games that you can play to practice different competences of your target language!",
            "No registration is needed to access the search tool neither to play our games! However, by signing up, "
            "you can participate in our games rankings and compete with other players."
        ]

        card_images = selenium_driver.find_elements(By.CLASS_NAME, "img-fluid")
        card_captions = selenium_driver.find_elements(By.CLASS_NAME, "card-text")

        assert len(card_captions) == 5
        for i in range(len(card_captions)):
            assert card_images[i].get_attribute("src") == live_server.url + "/static/" + image_names[i]
            assert card_captions[i].text == captions[i]