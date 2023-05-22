import random

from django.utils.crypto import get_random_string

from languageschool.models import Game, Language, Score, User

numberOfUsers = 20

for i in range(numberOfUsers):
    user = User.objects.create_user(username=get_random_string(100),
                                    email=get_random_string(20) + "@test.com",
                                    password="str0ng-p4ssw0rd")
    for language in Language.objects.all():
        for game in Game.objects.all():
            Score.objects.create(user=user, language=language, game=game, score=random.randint(10, 1000))
