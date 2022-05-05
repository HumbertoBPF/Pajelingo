from urllib.parse import urlencode
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.urls import reverse
from languageschool.models import Conjugation, Language, Word
import random

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

def vocabulary_game_setup(request):
    languages = Language.objects.all()

    return render(request, 'game/vocabulary_game/vocabulary_game_setup.html', {'languages':languages})

def vocabulary_game(request):
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
                    return render(request, "game/vocabulary_game/vocabulary_game.html", {"word":selected_word, "base_language":base_language})
                else:
                    messages.error(request, "The target and base languages must be different")
    # If some error was detected, go to the setup page
    return redirect('vocabulary_game_setup')

def vocabulary_game_verify_answer(request):
    if request.method == "POST":
        if request_contains(request.POST, ["word_to_translate_id", "translation_word", "base_language"]):
            word_to_translate_id = request.POST["word_to_translate_id"]
            translation_word = request.POST["translation_word"]
            base_language = get_object_or_404(Language, language_name = request.POST["base_language"])
            word_to_translate = get_object_or_404(Word, pk = word_to_translate_id)
            
            correct_translation = ""
            is_translation_correct = False
            for synonim in word_to_translate.synonym.all():
                if synonim.language == base_language:
                    # Getting the correct answer
                    if len(correct_translation) != 0:
                        correct_translation += ", "
                    correct_translation += str(synonim)
                    # Checking if the answer was correct (if the user provided a synonim and if the synonim is in the correct language)
                    if str(synonim) == translation_word:
                        is_translation_correct = True
            # Message of feedback for the user
            if is_translation_correct:
                messages.success(request, "Correct :)\n"+str(word_to_translate) + ": "+str(correct_translation))
            else:
                messages.error(request, "Wrong answer\n"+str(word_to_translate) + ": "+str(correct_translation))
            base_url = reverse('vocabulary_game')
            query_string =  urlencode({'base_language': str(base_language), 
                                'target_language': str(word_to_translate.language)})
            url = '{}?{}'.format(base_url, query_string)
            return redirect(url)
    # If some error was detected, go to the setup page
    return vocabulary_game_setup(request)

def article_game_setup(request):
    # For the article game, English is not a language available since it has a unique article
    languages = Language.objects.exclude(language_name = "English")

    return render(request, 'game/article_game/article_game_setup.html', {'languages': languages})

def article_game(request):
    if request.method == "GET":
        if request_contains(request.GET, ["language"]):
            language = request.GET["language"]
            # Verify if some language was chosen
            if len(language) == 0:
                messages.error(request, "You must choose a language")
            else:
                word = random.choice(Word.objects.filter(language=get_object_or_404(Language, language_name=language)).exclude(article = None))

                return render(request, 'game/article_game/article_game.html', {'word': word})
    # If some error was detected, go to setup page
    return redirect('article_game_setup')

def article_game_verify_answer(request):
    if request.method == "POST":
        if request_contains(request.POST, ["article", "word_id"]):
            user_answer = request.POST["article"]
            word_id = request.POST["word_id"]
            word = get_object_or_404(Word, pk = word_id)
            if word.article.article_name == user_answer:
                messages.success(request, 'Correct :)\n'+str(word))
            else:
                messages.error(request, 'Wrong answer\n'+str(word))
            base_url = reverse('article_game')
            query_string =  urlencode({'language': str(word.language)})
            url = '{}?{}'.format(base_url, query_string)
            return redirect(url)
    return article_game_setup(request)

def conjugation_game_setup(request):
    languages = Language.objects.all()

    return render(request, 'game/conjugation_game/conjugation_game_setup.html', {'languages':languages})

def conjugation_game(request):
    if request.method == "GET":
        if request_contains(request.GET, ["language"]):
            language = request.GET["language"]
            # Verify if some language was chosen
            if len(language) == 0:
                messages.error(request, "You must choose a language")
            else:
                word = random.choice(Word.objects.filter(language=get_object_or_404(Language, language_name=language)).filter(article = None))

                return render(request, 'game/conjugation_game/conjugation_game.html', {'word': word})
    # If some error was detected, go to setup page
    return redirect('conjugation_game_setup')

def conjugation_game_verify_answer(request):
    if request.method == "POST":
        if request_contains(request.POST, ["conjugation_1", "conjugation_2", "conjugation_3", "conjugation_4", "conjugation_5", "conjugation_6", "word_id"]):
            word_id = request.POST["word_id"]
            conjugation_1 = request.POST["conjugation_1"]
            conjugation_2 = request.POST["conjugation_2"]
            conjugation_3 = request.POST["conjugation_3"]
            conjugation_4 = request.POST["conjugation_4"]
            conjugation_5 = request.POST["conjugation_5"]
            conjugation_6 = request.POST["conjugation_6"]
            verb = get_object_or_404(Word, pk = word_id)
            language = verb.language
            conjugation = Conjugation.objects.filter(word = word_id).filter(tense = "present")[0]
            
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