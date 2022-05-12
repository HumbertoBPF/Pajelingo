from django.shortcuts import render
from django.core.paginator import Paginator
from languageschool.models import Meaning, Word
from django.db.models.functions import Lower


# Create your views here.
def request_contains(request_with_method, variables_required):
    dict_values = {}
    for variable in request_with_method:
        dict_values[variable] = True

    for variable_required in variables_required:
        if dict_values.get(variable_required) is None:
            return False

    return True

def index(request):
    return render(request, 'index.html')

def search(request):
    if request.method == "GET":
        if request_contains(request.GET, ["search"]):
            search = request.GET["search"]
            # Results containing the specified string
            search_results = Word.objects.filter(word_name__icontains = search).order_by(Lower('word_name'))
            # Pagination(getting page number and the results of the current page)
            paginator = Paginator(search_results, 12)
            page = request.GET.get('page')
            search_results_current_page = paginator.get_page(page)

            return render(request, 'search.html', {'search_results': search_results_current_page, 'search': search})
    
    return index(request)

def dictionary(request, word_id):
    meanings = Meaning.objects.filter(word = word_id)
    return render(request, 'meaning.html', {'meanings': meanings})
