from abc import ABC, abstractmethod

from django.contrib.auth.models import AbstractUser
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


class BadgeValidator(ABC):
    def __init__(self, languages, games, user):
        self.languages = languages
        self.games = games
        self.user = user

    @abstractmethod
    def validate(self):
        pass

class ExplorerBadgeValidator(BadgeValidator):
    def validate(self):
        for language in self.languages:
            explored_all_games = True

            for game in self.games:
                explored_all_games = \
                    explored_all_games and \
                    Score.objects.filter(game=game, language=language, user=self.user).exists()
                # No need to continue if a game has not been played yet
                if not explored_all_games:
                    break

            if explored_all_games:
                return True

        return False

class LanguageDomainValidator(BadgeValidator):
    def validate(self):
        more_than_100_points = 0

        for language in self.languages:
            more_than_100_points_in_language = True

            for game in self.games:
                more_than_100_points_in_language = \
                    more_than_100_points_in_language and \
                    Score.objects.filter(game=game, language=language, user=self.user, score__gte=100).exists()
                # If both validations have become false, we can stop iterating over the games for this language
                if not more_than_100_points_in_language:
                    break

            if more_than_100_points_in_language:
                more_than_100_points += 1

        return more_than_100_points


class Badge(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to=get_upload_to, blank=True)
    color = models.CharField(max_length=6)
    description = models.TextField(max_length=200)

    @staticmethod
    def update_badges(user):
        languages = Language.objects.all()
        games = Game.objects.all()

        explorer_badge_id = 1
        linguistic_mastery_badge_id = 2
        bilingual_badge_id = 3
        trilingual_badge_id = 4
        polyglot_badge_id = 5

        is_explorer = ExplorerBadgeValidator(languages, games, user).validate()
        more_than_100_points = LanguageDomainValidator(languages, games, user).validate()

        current_badges = user.badges.values_list("id", flat=True)

        list_new_badges = []
        print("HELLO", is_explorer)
        if is_explorer and (explorer_badge_id not in current_badges):
            list_new_badges.append(explorer_badge_id)

        if more_than_100_points > 0 and (linguistic_mastery_badge_id not in current_badges):
            list_new_badges.append(linguistic_mastery_badge_id)

        if more_than_100_points > 1 and (bilingual_badge_id not in current_badges):
            list_new_badges.append(bilingual_badge_id)

        if more_than_100_points > 2 and (trilingual_badge_id not in current_badges):
            list_new_badges.append(trilingual_badge_id)

        if more_than_100_points > 3 and (polyglot_badge_id not in current_badges):
            list_new_badges.append(polyglot_badge_id)

        user.badges.add(*list_new_badges)
        print("HELLO", list_new_badges)
        return list_new_badges

    def __str__(self):
        return self.name


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
    favorite_words = models.ManyToManyField(Word, blank=True)
    picture = models.ImageField(upload_to=get_upload_to, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    badges = models.ManyToManyField(Badge, blank=True)

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
