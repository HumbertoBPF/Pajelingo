import random
from urllib.parse import urlencode
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from languageschool.models import Conjugation, Language, Word
from django.contrib import messages
from languageschool.views.general import request_contains


def conjugation_game_setup(request):
    languages = Language.objects.all()

    return render(request, 'games/conjugation_game/conjugation_game_setup.html', {'languages':languages})

def conjugation_game(request):
    if request.method == "GET":
        if request_contains(request.GET, ["language"]):
            language = request.GET["language"]
            # Verify if some language was chosen
            if len(language) == 0:
                messages.error(request, "You must choose a language")
            else:
                # Picks a verb and a conjugation
                verb = random.choice(Word.objects.filter(language=get_object_or_404(Language, language_name=language)).filter(article = None))
                conjugation = random.choice(Conjugation.objects.filter(word = verb.id))

                return render(request, 'games/conjugation_game/conjugation_game.html', {'word': verb, 'tense': conjugation.tense})
    # If some error was detected, go to setup page
    return redirect('conjugation_game_setup')

def conjugation_game_verify_answer(request):
    if request.method == "POST":
        if request_contains(request.POST, ["conjugation_1", "conjugation_2", "conjugation_3", "conjugation_4", "conjugation_5", "conjugation_6", "word_id", "tense"]):
            # Get verb, verbal tense and language
            word_id = request.POST["word_id"]
            tense = request.POST["tense"]
            verb = get_object_or_404(Word, pk = word_id)
            language = verb.language
            # Get answers of the user
            conjugation_1 = request.POST["conjugation_1"]
            conjugation_2 = request.POST["conjugation_2"]
            conjugation_3 = request.POST["conjugation_3"]
            conjugation_4 = request.POST["conjugation_4"]
            conjugation_5 = request.POST["conjugation_5"]
            conjugation_6 = request.POST["conjugation_6"]
            conjugation = Conjugation.objects.filter(word = word_id).filter(tense = tense)[0]
            # Get the correct answer and verifying user's answer
            correct_answer = language.personal_pronoun_1 + " " + conjugation.conjugation_1 + "\n" + \
                             language.personal_pronoun_2 + " " + conjugation.conjugation_2 + "\n" + \
                             language.personal_pronoun_3 + " " + conjugation.conjugation_3 + "\n" + \
                             language.personal_pronoun_4 + " " + conjugation.conjugation_4 + "\n" + \
                             language.personal_pronoun_5 + " " + conjugation.conjugation_5 + "\n" + \
                             language.personal_pronoun_6 + " " + conjugation.conjugation_6 + "\n"
            if conjugation_1 == conjugation.conjugation_1 and conjugation_2 == conjugation.conjugation_2 \
                and conjugation_3 == conjugation.conjugation_3 and conjugation_4 == conjugation.conjugation_4 \
                and conjugation_5 == conjugation.conjugation_5 and conjugation_6 == conjugation.conjugation_6:
                messages.success(request, "Correct :)\n"+correct_answer)
            else:
                messages.error(request, "Wrong answer\n"+correct_answer)
            base_url = reverse('conjugation_game')
            query_string =  urlencode({'language': str(verb.language)})
            url = '{}?{}'.format(base_url, query_string)
            return redirect(url)
    return conjugation_game_setup(request)