# Create your views here.
def request_contains(request_with_method, variables_required):
    '''Verifies if a request method contains the variables whose name is specified as a list in the 'variables_required' argument.'''
    dict_values = {}
    for variable in request_with_method:
        dict_values[variable] = True

    for variable_required in variables_required:
        if dict_values.get(variable_required) is None:
            return False

    return True