import random
from urllib.parse import urlencode
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from languageschool.models import Category, Conjugation, Language, Score, Word, Game
from django.contrib import messages
from languageschool.utils import request_contains
from languageschool.game import GameView


class ConjugationGame(GameView):
    def get_game_model():
        return get_object_or_404(Game, id=3)

    def setup(request):
        languages = Language.objects.all()

        return render(request, 'games/conjugation_game/conjugation_game_setup.html', {'languages':languages})

    def play(request):
        if request.method == "GET":
            if request_contains(request.GET, ["language"]):
                language = request.GET["language"]
                # Verify if some language was chosen
                if len(language) == 0:
                    messages.error(request, "You must choose a language")
                else:
                    # Picks a verb and a conjugation
                    category = get_object_or_404(Category, category_name = "verbs")
                    verb = random.choice(Word.objects.filter(language=get_object_or_404(Language, language_name=language)).filter(category = category))
                    conjugation = random.choice(Conjugation.objects.filter(word = verb.id))

                    return render(request, 'games/conjugation_game/conjugation_game.html', {'word': verb, 'tense': conjugation.tense})
        # If some error was detected, go to setup page
        return redirect('conjugation_game_setup')
    
    def verify_answer(request):
        if request.method == "POST":
            if request_contains(request.POST, ["conjugation_1", "conjugation_2", "conjugation_3", "conjugation_4", "conjugation_5", "conjugation_6", "word_id", "tense"]):
                # Get verb, verbal tense and language
                word_id = request.POST["word_id"]
                tense = request.POST["tense"]
                verb = get_object_or_404(Word, pk = word_id)
                language = verb.language
                # Get answers of the user
                conjugation_1 = request.POST["conjugation_1"].strip()
                conjugation_2 = request.POST["conjugation_2"].strip()
                conjugation_3 = request.POST["conjugation_3"].strip()
                conjugation_4 = request.POST["conjugation_4"].strip()
                conjugation_5 = request.POST["conjugation_5"].strip()
                conjugation_6 = request.POST["conjugation_6"].strip()
                conjugation = Conjugation.objects.filter(word = word_id).filter(tense = tense)[0]
                # Get the correct answer and verifying user's answer
                correct_answer = language.personal_pronoun_1 + " " + conjugation.conjugation_1 + "\n" + \
                                language.personal_pronoun_2 + " " + conjugation.conjugation_2 + "\n" + \
                                language.personal_pronoun_3 + " " + conjugation.conjugation_3 + "\n" + \
                                language.personal_pronoun_4 + " " + conjugation.conjugation_4 + "\n" + \
                                language.personal_pronoun_5 + " " + conjugation.conjugation_5 + "\n" + \
                                language.personal_pronoun_6 + " " + conjugation.conjugation_6 + "\n"
                # Verifying user's answer
                if conjugation_1 == conjugation.conjugation_1 and conjugation_2 == conjugation.conjugation_2 \
                    and conjugation_3 == conjugation.conjugation_3 and conjugation_4 == conjugation.conjugation_4 \
                    and conjugation_5 == conjugation.conjugation_5 and conjugation_6 == conjugation.conjugation_6:
                    # Increment score when getting the right answer
                    score = Score.increment_score(request, language, ConjugationGame.get_game_model())
                    message_string = "Correct :)\n"+correct_answer
                    if score is not None:
                        message_string += "\nYour score is "+str(score.score)
                    messages.success(request, message_string)
                else:
                    messages.error(request, "Wrong answer\n"+correct_answer)
                base_url = reverse('conjugation_game')
                query_string =  urlencode({'language': str(verb.language)})
                url = '{}?{}'.format(base_url, query_string)
                return redirect(url)
        return ConjugationGame.setup(request)