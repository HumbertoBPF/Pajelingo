from django.core.paginator import Paginator
from django.db.models import Sum
from django.db.models.functions import Lower
from django.shortcuts import render
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
def about_us(request):
    return render(request, 'about_us.html')

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
    language_name = request.GET.get("language")
    language = Language.objects.filter(language_name=language_name).first()
    # List of languages for the select field
    languages = Language.objects.all()

    if language is None:
        language = languages.first()

    scores = None
    if language is not None:
        scores = Score.objects.filter(language=language).values('user__username') \
            .annotate(score=Sum('score')).order_by('-score')
    # Only the top 10 of each ranking is shown
    context = {
        "languages": languages,
        "language": language,
        "scores": scores[:10]
    }
    # If the users are logged in, their position in the ranking is shown
    if request.user.is_authenticated:
        for i, item in enumerate(scores):
            if item["user__username"] == request.user.username:
                context["my_position"] = i + 1
                context["my_score"] = item
                break

    return render(request, 'games/rankings.html', context)
