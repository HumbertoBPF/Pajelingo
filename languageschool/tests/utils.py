import base64
import io

from django.contrib import auth
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer


def is_user_authenticated(client, user):
    """
    Verifies if the specified user is authenticated in the current session.

    :param client: Django client fixture
    :param user: instance of a user that we want to check that is authenticated
    :type user: User

    :return: boolean indicating if the specified user is authenticated
    """
    return auth.get_user(client).username == user.username


def get_basic_auth_header(username, password):
    credentials = base64.b64encode(f'{username}:{password}'.encode('utf-8'))
    return 'Basic {}'.format(credentials.decode('utf-8'))


def deserialize_data(data):
    """
    Deserialize the specified data payload into a dictionary.
    :param data: data to be deserialized

    :return: dictionary corresponding to the deserialized data payload.
    """
    json = JSONRenderer().render(data)
    stream = io.BytesIO(json)
    return JSONParser().parse(stream)


def is_model_objects_equal_to_dict_array(objects, dict_array, comparer):
    """
    Verifies if a dictionary array is equivalent to an array of objects using the specified comparer.

    :param objects: list of objects
    :type objects: list
    :param dict_array: list of dictionaries
    :type dict_array: list
    :param comparer: comparer object

    :return: boolean indicating if the list of objects and if the list of dictionaries are equivalent.
    """
    id_to_object = {}

    for obj in objects:
        id_to_object[obj.id] = obj

    for item in dict_array:
        obj = id_to_object.get(item.get("id"))

        if obj is None or not(comparer.are_equal(obj, item)):
            return False

        del id_to_object[item.get("id")]

    return True


def get_users(accounts):
    """
    Gets list of users associated with the specified list of accounts (an account here is a tuple with the user object
    and its corresponding password).
    :param accounts: list of tuples, each one containing a user object and its associated password
    :type accounts: list

    :return: list of users
    """
    users = []
    for user, password in accounts:
        users.append(user)

    return users
