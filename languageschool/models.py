from django.contrib.auth.models import AbstractUser
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _


def get_upload_to(instance, filename):
    # file will be uploaded to models/Language/<id>/<filename>
    return 'images/models/{}/{}/{}'.format(instance.__class__.__name__, instance.id, filename)


class Game(models.Model):
    game_name = models.CharField(max_length=30, unique=True)
    android_game_activity = models.CharField(max_length=100)
    image = models.ImageField(upload_to=get_upload_to, blank=True)
    link = models.CharField(max_length=100)
    instructions = models.TextField(blank=True)

    def __str__(self):
        return self.game_name


class Language(models.Model):
    language_name = models.CharField(max_length=30, unique=True)
    personal_pronoun_1 = models.CharField(max_length=30, blank=True, null=True)
    personal_pronoun_2 = models.CharField(max_length=30, blank=True, null=True)
    personal_pronoun_3 = models.CharField(max_length=30, blank=True, null=True)
    personal_pronoun_4 = models.CharField(max_length=30, blank=True, null=True)
    personal_pronoun_5 = models.CharField(max_length=30, blank=True, null=True)
    personal_pronoun_6 = models.CharField(max_length=30, blank=True, null=True)
    flag_image = models.ImageField(upload_to=get_upload_to, blank=True)

    def __str__(self):
        return self.language_name


class Category(models.Model):
    category_name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name_plural = "Categories"


class Article(models.Model):
    article_name = models.CharField(max_length=10)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)

    def __str__(self):
        return "{} ({})".format(self.article_name, self.language)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['article_name', 'language'],
                name='article_unique_constraint'
            )
        ]


class Word(models.Model):
    word_name = models.CharField(max_length=30)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    synonyms = models.ManyToManyField("self", blank=True)
    image = models.ImageField(upload_to=get_upload_to, blank=True)

    def __str__(self):
        article = ""
        if self.article is not None:
            article = "{}".format(self.article.article_name)
            if not(self.article.article_name.endswith("'")):
                article += " "
        return "{}{}".format(article, self.word_name)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['word_name', 'language', 'article'],
                name='word_unique_constraint'
            )
        ]


class User(AbstractUser):
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[UnicodeUsernameValidator(), MinLengthValidator(8)],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    email = models.EmailField(_("email address"), unique=True)
    password = models.CharField(_("password"), max_length=128, validators=[validate_password])
    favorite_words = models.ManyToManyField(Word, blank=True)
    picture = models.ImageField(upload_to=get_upload_to, blank=True)
    bio = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return str(self.username)


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
        return "{} - {}".format(self.word.word_name, self.tense)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['word', 'tense'],
                name='conjugation_unique_constraint'
            )
        ]


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

            try:
                score = Score.objects.get(user=request.user, language=language, game=game)
                score.score += 1
                score.save()
            except Score.DoesNotExist:
                score = Score.objects.create(user=request.user, language=language, game=game, score=1)

            return score

        return None

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'language', 'game'],
                name='score_unique_constraint'
            )
        ]


class GameRound(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    round_data = models.JSONField()

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'game'],
                name='game_round_unique_constraint'
            )
        ]
