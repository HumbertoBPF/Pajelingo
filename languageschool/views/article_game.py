import random
from urllib.parse import urlencode
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from languageschool.models import Language, Word
from django.contrib import messages
from languageschool.views.general import request_contains


def article_game_setup(request):
    # For the article game, English is not a language available since it has a unique article
    languages = Language.objects.exclude(language_name = "English")

    return render(request, 'games/article_game/article_game_setup.html', {'languages': languages})

def article_game(request):
    if request.method == "GET":
        if request_contains(request.GET, ["language"]):
            language = request.GET["language"]
            # Verify if some language was chosen
            if len(language) == 0:
                messages.error(request, "You must choose a language")
            else:
                word = random.choice(Word.objects.filter(language=get_object_or_404(Language, language_name=language)).exclude(article = None))

                return render(request, 'games/article_game/article_game.html', {'word': word})
    # If some error was detected, go to setup page
    return redirect('article_game_setup')

def article_game_verify_answer(request):
    if request.method == "POST":
        if request_contains(request.POST, ["article", "word_id"]):
            # Get word chosen and user's answer
            user_answer = request.POST["article"]
            word_id = request.POST["word_id"]
            word = get_object_or_404(Word, pk = word_id)
            # Verifying user's answer
            if word.article.article_name == user_answer:
                messages.success(request, 'Correct :)\n'+str(word))
            else:
                messages.error(request, 'Wrong answer\n'+str(word))
            base_url = reverse('article_game')
            query_string =  urlencode({'language': str(word.language)})
            url = '{}?{}'.format(base_url, query_string)
            return redirect(url)
    return article_game_setup(request)