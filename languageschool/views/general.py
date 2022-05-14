from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from languageschool.models import Language, Meaning, Score, Word
from django.db.models.functions import Lower
from django.db.models import Sum

# Create your views here.
def request_contains(request_with_method, variables_required):
    dict_values = {}
    for variable in request_with_method:
        dict_values[variable] = True

    for variable_required in variables_required:
        if dict_values.get(variable_required) is None:
            return False

    return True

def create_score_if_not_exist(request, language, game):
    '''Create a score if there is no score for this user in this game'''
    if request.user.is_authenticated:
        score = Score.objects.filter(user = request.user, language = language, game = game)
        if len(score) == 0:
            score = Score(user = request.user, language = language, game = game, score = 0)
            score.save()

# Increment score when getting the right answer
def increment_score(request, language, game):
    '''Function to increment the score of a game when getting a correct answer'''
    if request.user.is_authenticated:
        score = Score.objects.filter(user = request.user, language = language, game = game).latest('id')
        score.score += 1
        score.save()

        return score
    
    return None

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

def rankings(request):
    # Show the sum of the scores in all the games for each user
    general_scores = Score.objects.values('user__username').annotate(general_score = Sum('score')).order_by('-general_score')
    # List of languages for the select field
    languages = Language.objects.all()
    scores_dict = {'general_scores': general_scores, 'languages': languages}
    # If some language was specified, add the ranking associated with this language
    if request.method == "GET":
        if request_contains(request.GET, ["language"]):
            language_name = request.GET["language"]
            language = get_object_or_404(Language, language_name = language_name)
            scores_in_language = Score.objects.filter(language = language).values('user__username').annotate(score = Sum('score')).order_by('-score')
            scores_dict['scores_in_language'] = scores_in_language
            scores_dict['language'] = language
    return render(request, 'games/rankings.html', scores_dict)