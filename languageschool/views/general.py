from django.core.paginator import Paginator
from django.db.models import Sum
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from languageschool.models import Language, Meaning, Score, Word
from languageschool.utils import request_contains


@require_GET
def index(request):
    return render(request, 'index.html')

@require_GET
def search(request):
    languages = Language.objects.all()
    return render(request, 'search_tool/search_form.html', {"languages": languages})

@require_GET
def search_done(request):
    if request_contains(request.GET, ["search"]):
        search_pattern = request.GET["search"]
        languages = []
        for language in Language.objects.all():
            if request.GET.get(language.language_name) == "True":
                languages.append(language)
        # Results containing the specified string
        search_results = Word.objects\
            .filter(word_name__icontains=search_pattern, language__in=languages).order_by(Lower('word_name'))
        # Pagination(getting page number and the results of the current page)
        paginator = Paginator(search_results, 12)
        page = request.GET.get('page')
        search_results_current_page = paginator.get_page(page)

        return render(request, 'search_tool/search.html', {'search_results': search_results_current_page, 'base_url': request.get_full_path().split("&page")[0]})
    return index(request)

@require_GET
def meaning(request, word_id):
    meanings = Meaning.objects.filter(word=word_id)
    return render(request, 'search_tool/meaning.html', {'meanings': meanings})

@require_GET
def rankings(request):
    # List of languages for the select field
    languages = Language.objects.all()
    scores_dict = {'languages': languages}
    # If some language was specified, add the ranking associated with this language
    if request_contains(request.GET, ["language"]) and len(request.GET["language"]) != 0:
        language_name = request.GET["language"]
        language = get_object_or_404(Language, language_name=language_name)
        scores = Score.objects.filter(language=language).values('user__username')\
            .annotate(score=Sum('score')).order_by('-score')
        scores_dict['language'] = language
        # Otherwise, show the general ranking
    else:
        # Show the sum of the scores in all the games for each user
        scores = Score.objects.values('user__username').annotate(score=Sum('score')).order_by('-score')
    # If the users are logged in, their position in the ranking is shown
    if request.user.is_authenticated:
        for i, item in enumerate(scores):
            if item['user__username'] == request.user.username:
                scores_dict['my_position'] = i + 1
                scores_dict['my_score'] = item
                break
    # Only the top 10 of each ranking is shown
    scores_dict['scores'] = scores[:10]

    return render(request, 'games/rankings.html', scores_dict)
