import math
import random
from urllib.parse import urlencode

import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status

from languageschool.models import User
from languageschool.tests.utils import assert_badges

SEARCH_ACCOUNTS_URL = reverse("search-accounts-api")


def assert_response(response, q, page, number_accounts):
    query = "" if (q is None) else q

    expected_number_pages = math.ceil(number_accounts / 10)

    data = response.data

    results = data.get("results")
    count = data.get("count")
    previous_page = data.get("previous")
    next_page = data.get("next")

    expected_number_accounts = 10

    if (page == expected_number_pages) and (number_accounts % 10 != 0):
        expected_number_accounts = number_accounts % 10

    assert len(results) == expected_number_accounts

    for result in results:
        username = result.get("username")
        bio = result.get("bio")
        badges = result.get("badges")

        assert username is not None
        assert bio is not None
        user = User.objects.get(username=username)

        assert user.bio == bio
        assert len(badges) == 2

        assert_badges(result.get("badges"), user)

        assert query.lower() in username.lower()

    assert count == number_accounts

    if page == 1:
        assert previous_page is None

    if page == expected_number_pages:
        assert next_page is None


@pytest.mark.django_db
def test_search_accounts_no_query_param(api_client, account):
    number_accounts = random.randint(11, 30)
    account(n=number_accounts)
    accounts_dict = {}

    expected_number_pages = math.ceil(number_accounts/10)

    for i in range(expected_number_pages):
        page = i + 1

        query_params = {
            "page": page
        }
        query_string = urlencode(query_params)
        url = "{}?{}".format(SEARCH_ACCOUNTS_URL, query_string)

        response = api_client.get(url)

        assert_response(response, None, page, number_accounts)

        for result in response.data.get("results"):
            username = result.get("username")
            accounts_dict[username] = True

    assert len(accounts_dict) == number_accounts


@pytest.mark.django_db
def test_search_accounts_with_query_param(api_client, account):
    account(n=random.randint(11, 30))

    q = get_random_string(1)

    number_matched_accounts = User.objects.filter(username__icontains=q).count()
    accounts_dict = {}

    expected_number_pages = math.ceil(number_matched_accounts/10)

    for i in range(expected_number_pages):
        page = i + 1

        query_params = {
            "page": page,
            "q": q
        }
        query_string = urlencode(query_params)
        url = "{}?{}".format(SEARCH_ACCOUNTS_URL, query_string)

        response = api_client.get(url)

        assert_response(response, q, page, number_matched_accounts)

        for result in response.data.get("results"):
            username = result.get("username")
            accounts_dict[username] = True

    assert len(accounts_dict) == number_matched_accounts


@pytest.mark.django_db
def test_search_account_not_found(api_client):
    username = get_random_string(random.randint(1, 10))
    url = reverse("account-api", kwargs={"username": username})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_search_account(api_client, account):
    user, password = account()[0]
    url = reverse("account-api", kwargs={"username": user.username})

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    response_body = response.data
    assert response_body.get("username") == user.username
    assert response_body.get("picture") is None
    assert response_body.get("bio") == user.bio
    assert len(response_body.get("badges")) == 2
    assert_badges(response_body.get("badges"), user)
