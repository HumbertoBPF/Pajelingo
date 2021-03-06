import random
from urllib.parse import urlencode
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from languageschool.models import Language, Score, Word, Game
from django.contrib import messages
from languageschool.utils import request_contains
from languageschool.game import GameView


class VocabularyGame(GameView):
    def get_game_model():
        return get_object_or_404(Game, id=1)

    def setup(request):
        languages = Language.objects.all()

        return render(request, 'games/vocabulary_game/vocabulary_game_setup.html', {'languages':languages})

    def play(request):
        if request.method == "GET":
            if request_contains(request.GET, ["base_language","target_language"]):
                base_language = request.GET["base_language"]
                target_language = request.GET["target_language"]
                # Verifying if a base language and a target language were selected
                if len(base_language) == 0:
                    messages.error(request, "Please, select a base language")
                elif len(target_language) == 0:
                    messages.error(request, "Please, select a target language")
                else:
                    # Verifying if the selected languages are equal
                    if base_language != target_language:
                        # Validating the base_language (check if it is a valid language, if not it returns a 404 error)
                        base_language = get_object_or_404(Language, language_name = base_language)
                        # Picking all the words corresponding to the target language
                        words_list = Word.objects.filter(language = get_object_or_404(Language, language_name = target_language))
                        selected_word = random.choice(words_list)
                        return render(request, "games/vocabulary_game/vocabulary_game.html", {"word":selected_word, "base_language":base_language})
                    else:
                        messages.error(request, "The target and base languages must be different")
        # If some error was detected, go to the setup page
        return redirect('vocabulary_game_setup')
    
    def verify_answer(request):
        if request.method == "POST":
            if request_contains(request.POST, ["word_to_translate_id", "translation_word", "base_language"]):
                # Getting word to translate, language of the translation and user's answer
                word_to_translate_id = request.POST["word_to_translate_id"]
                translation_word = request.POST["translation_word"].strip()
                base_language = get_object_or_404(Language, language_name = request.POST["base_language"])
                word_to_translate = get_object_or_404(Word, pk = word_to_translate_id)
                # Verifying user's answer
                correct_translation = ""
                is_translation_correct = False
                for synonim in word_to_translate.synonyms.all():
                    if synonim.language == base_language:
                        # Getting the correct answer
                        if len(correct_translation) != 0:
                            correct_translation += ", "
                        correct_translation += synonim.word_name
                        # Checking if the answer was correct (if the user provided a synonim and if the synonim is in the correct language)
                        if synonim.word_name == translation_word:
                            is_translation_correct = True
                # Message of feedback for the user
                if is_translation_correct:
                    # Increment score when getting the right answer
                    score = Score.increment_score(request, word_to_translate.language, VocabularyGame.get_game_model())
                    message_string = "Correct :)\n" + word_to_translate.word_name + ": " + correct_translation
                    if score is not None:
                        message_string += "\nYour score is "+str(score.score)
                    messages.success(request, message_string)
                else:
                    messages.error(request, "Wrong answer\n" + word_to_translate.word_name + ": " + correct_translation)
                base_url = reverse('vocabulary_game')
                query_string =  urlencode({'base_language': str(base_language), 
                                    'target_language': str(word_to_translate.language)})
                url = '{}?{}'.format(base_url, query_string)
                return redirect(url)
        # If some error was detected, go to the setup page
        return VocabularyGame.setup(request)
    