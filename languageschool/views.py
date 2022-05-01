from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from languageschool.models import Language, Word
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

    return render(request, 'vocabulary_game_setup.html', {'languages':languages})

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
                    # Validating the base_language (check if it is a valid language)
                    base_language = get_object_or_404(Language, language_name = base_language)
                    # Picking all the words corresponding to the target language
                    words_list = Word.objects.filter(language = get_object_or_404(Language, language_name = target_language))
                    selected_word = random.choice(words_list)
                    return render(request, "vocabulary_game.html", {"word":selected_word, "base_language":base_language})
                else:
                    messages.error(request, "The target and base languages must be different")
    # If some error was detect, go to the setup page
    return vocabulary_game_setup(request)

def vocabulary_game_verify_answer(request):
    if request.method == "POST":
        if request_contains(request.POST, ["word_to_translate_id", "translation_word", "base_language"]):
            word_to_translate_id = request.POST["word_to_translate_id"]
            translation_word = request.POST["translation_word"]
            base_language = get_object_or_404(Language, language_name = request.POST["base_language"])
            word_to_translate = get_object_or_404(Word, pk = word_to_translate_id)
            is_translation_correct = False
            for synonim in word_to_translate.synonym.all():
                if synonim.language == base_language and str(synonim) == translation_word:
                    is_translation_correct = True
                    break
            if is_translation_correct:
                messages.success(request, "Correct :)")
            else:
                messages.error(request, "Wrong answer, don't give up and ask help for Google Translator if necessary")
            return render(request, "vocabulary_game.html", 
                {"word": word_to_translate, 
                "base_language": base_language, 
                "last_answer": translation_word ,
                "is_translation_correct": is_translation_correct})
    # If some error was detect, go to the setup page
    return vocabulary_game_setup(request)