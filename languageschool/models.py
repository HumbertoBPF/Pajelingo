from django.contrib.auth.models import User
from django.db import models


class Game(models.Model):
    game_name = models.CharField(max_length=30, unique=True, null=True, blank=True)
    android_game_activity = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.game_name)


class Language(models.Model):
    language_name = models.CharField(max_length=30, unique=True)
    personal_pronoun_1 = models.CharField(max_length=30, blank=True, null=True)
    personal_pronoun_2 = models.CharField(max_length=30, blank=True, null=True)
    personal_pronoun_3 = models.CharField(max_length=30, blank=True, null=True)
    personal_pronoun_4 = models.CharField(max_length=30, blank=True, null=True)
    personal_pronoun_5 = models.CharField(max_length=30, blank=True, null=True)
    personal_pronoun_6 = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return self.language_name


class Category(models.Model):
    category_name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.category_name


class Article(models.Model):
    article_name = models.CharField(max_length=10)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)

    def __str__(self):
        return self.article_name + " (" + str(self.language) + ")"


class Word(models.Model):
    word_name = models.CharField(max_length=30)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, blank=True, null=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    synonyms = models.ManyToManyField("self", blank=True)
    image = models.ImageField(upload_to='images/%d/%m/%Y', blank=True)

    def __str__(self):
        return ((str(self.article.article_name) + " ") if (self.article is not None) else "") + self.word_name


class Meaning(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    meaning = models.TextField()

    def __str__(self):
        return str(self.word)


class Conjugation(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    conjugation_1 = models.CharField(max_length=30)
    conjugation_2 = models.CharField(max_length=30)
    conjugation_3 = models.CharField(max_length=30)
    conjugation_4 = models.CharField(max_length=30)
    conjugation_5 = models.CharField(max_length=30)
    conjugation_6 = models.CharField(max_length=30)
    tense = models.CharField(max_length=30)

    def __str__(self):
        return self.word.word_name + " " + self.tense


class Score(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    score = models.PositiveBigIntegerField()

    @staticmethod
    def increment_score(request, language, game):
        """
        Function to increment the score of a game when getting a correct answer.

        :param request: Django request object
        :param language: language attribute of the concerned score
        :param game: game attribute of the concerned score

        :return: if the update is performed, the updated score is returned. Otherwise, None is returned.
        """
        if request.user.is_authenticated:
            score = Score.objects.filter(user=request.user, language=language, game=game)

            if len(score) == 0:
                score = Score(user=request.user, language=language, game=game, score=1)
            else:
                score = score.latest('id')
                score.score += 1

            score.save()
            return score

        return None


class AppUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='images/%d/%m/%Y', blank=True)

    def __str__(self):
        return str(self.user)
