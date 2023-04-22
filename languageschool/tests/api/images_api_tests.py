import base64
import random
from urllib.parse import urlencode

import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status

from pajelingo import settings

BASE_URL = reverse("public-images-api")


@pytest.mark.django_db
def test_image_api_without_image_url(api_client):
    """
    Testing that the endpoint returns 400 Bad Request if the url parameter is not specified.
    """
    response = api_client.get(BASE_URL)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_image_api_with_invalid_resource(api_client):
    """
    Testing that the endpoint returns 404 Not Found if an invalid resource URL is specified.
    """
    query_string = urlencode({"url": get_random_string(random.randint(1, 10))})
    url = "{}?{}".format(BASE_URL, query_string)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_image_api_with_unauthorized_resource(api_client):
    """
    Testing that the endpoint returns 403 Forbidden if a resource whose URL starts with /media/images/models is
    requested.
    """
    query_string = urlencode({"url": "/media/images/models/AppUser/{}"
                             .format(get_random_string(random.randint(1, 10)))})
    url = "{}?{}".format(BASE_URL, query_string)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_image_api_successful_request(api_client):
    """
    Testing that the endpoint returns 403 Forbidden if a resource whose URL starts with /media/images/models is
    requested.
    """
    url_resource =  "/media/images/models/TestModel/test.png"
    query_string = urlencode({"url": url_resource})
    url = "{}?{}".format(BASE_URL, query_string)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

    with open(settings.MEDIA_ROOT + url_resource.split("/media")[1], "rb") as img:
        expected_image_base64 = base64.b64encode(img.read())
        assert response.data.get("image") == expected_image_base64
