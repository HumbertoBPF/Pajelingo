from django.shortcuts import redirect


def request_contains(method, params):
    """
    Verifies if a request method contains the variables whose name is specified as a list in the 'variables_required' argument.

    :param method: HTTP request method
    :type method: dict
    :param params: list of parameters that we want to verify that are contained in the request
    :type params: list

    :return: boolean indicating if all the specified parameters are contained in the request
    """
    dict_values = {}
    for variable in method:
        dict_values[variable] = True

    for variable_required in params:
        if dict_values.get(variable_required) is None:
            return False

    return True


def require_authentication(func):
    def check_authentication(*args, **kwargs):
        if args[0].user.is_authenticated:
            return func(*args, **kwargs)
        return redirect('account-login')
    return check_authentication