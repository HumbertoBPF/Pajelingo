from django.shortcuts import redirect, render
from django.contrib import messages

from languageschool.models import Language

# Create your views here.

def index(request):
    return render(request, 'index.html')

def vocabulary_game_setup(request):
    languages = Language.objects.all()
    languages_list = {'languages':languages}

    return render(request, 'vocabulary_game_setup.html', languages_list)

def vocabulary_game(request):
    if request.method == "GET":
        if "base_language" in request.GET and "target_language" in request.GET:
            base_language = request.GET["base_language"]
            target_language = request.GET["target_language"]
            print("base_language =  "+base_language)
            print("target_language = "+target_language)
            # Verifying if a base language and a target language were selected
            if len(base_language) == 0:
                messages.error(request, "Please, select a base language")
            elif len(target_language) == 0:
                messages.error(request, "Please, select a target language")
            else:
                # Verifying if the selected languages are equal
                if base_language != target_language:
                    return redirect("vocabulary_game/setup")
                else:
                    messages.error(request, "The target and base languages must be different")
    # If some error was detect, go to the setup page
    return vocabulary_game_setup(request)
