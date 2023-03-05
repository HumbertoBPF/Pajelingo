import base64

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from languageschool.models import Article, Category, Conjugation, Language, Meaning, Score, Word, Game
from pajelingo.validators.validators import validate_email, validate_username


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'


class LanguageSerializer(serializers.ModelSerializer):
    flag_image = serializers.SerializerMethodField()
    flag_image_uri = serializers.SerializerMethodField()

    class Meta:
        model = Language
        fields = '__all__'

    def get_flag_image(self, obj):
        if obj.flag_image:
            try:
                img = obj.flag_image.open("rb")
                return base64.b64encode(img.read())
            except FileNotFoundError as e:
                print(e)

    def get_flag_image_uri(self, obj):
        if obj.flag_image:
            return obj.flag_image.url


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ArticleSerializer(serializers.ModelSerializer):
    language = serializers.ReadOnlyField(source='language.language_name')

    class Meta:
        model = Article
        fields = '__all__'


class WordSerializer(serializers.ModelSerializer):
    language = serializers.ReadOnlyField(source='language.language_name')
    category = serializers.ReadOnlyField(source='category.category_name')
    image = serializers.SerializerMethodField()

    class Meta:
        model = Word
        fields = '__all__'

    def get_image(self, obj):
        if obj.image:
            return obj.image.url


class MeaningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meaning
        fields = '__all__'


class ConjugationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conjugation
        fields = '__all__'


class RankingsSerializer(serializers.Serializer):
    position = serializers.IntegerField()
    user = serializers.CharField(source="user__username")
    score = serializers.IntegerField()


class ListScoreSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    language = serializers.ReadOnlyField(source='language.language_name')
    game = serializers.ReadOnlyField(source='game.id')

    class Meta:
        model = Score
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    class Meta:
        model = User
        fields = ("email", "username", "password")

    def create(self, validated_data):
        username = validated_data.get("username")
        email = validated_data.get("email")
        password = validated_data.get("password")

        user = User.objects.create_user(email=email, username=username, password=password)
        user.is_active = False
        user.save()

        return user

    def update(self, instance, validated_data):
        username = validated_data.get("username")
        email = validated_data.get("email")
        password = validated_data.get("password")

        instance.username = username
        instance.email = email
        instance.set_password(password)
        instance.save()

        return instance

    def validate_email(self, value):
        validate_email(value, self.instance)
        return value

    def validate_username(self, value):
        validate_username(value)
        return value

    def validate_password(self, value):
        validate_password(value)
        return value


class ScoreSerializer(serializers.Serializer):
    language = serializers.CharField()
    game = serializers.IntegerField()

    def create(self, validated_data):
        language = get_object_or_404(Language, language_name=validated_data.get("language"))
        game = get_object_or_404(Game, pk=validated_data.get("game"))
        score = Score(user=self.context.get("user"), language=language, game=game, score=1)
        score.save()
        return score

    def update(self, instance, validated_data):
        instance.score += 1
        instance.save()
        return instance


class ArticleGameAnswerSerializer(serializers.Serializer):
    word_id = serializers.IntegerField()
    answer = serializers.CharField(allow_blank=True)

    def save(self, **kwargs):
        word_id = self.validated_data.get("word_id")
        answer = self.validated_data.get("answer")

        word = get_object_or_404(Word, pk=word_id)

        return word.article.article_name == answer, str(word)


class VocabularyGameAnswerSerializer(serializers.Serializer):
    word_id = serializers.IntegerField()
    base_language = serializers.CharField()
    answer = serializers.CharField(allow_blank=True)

    def save(self, **kwargs):
        word_id = self.validated_data.get("word_id")
        base_language = self.validated_data.get("base_language")
        answer = self.validated_data.get("answer")

        base_language = get_object_or_404(Language, language_name=base_language)
        word_to_translate = get_object_or_404(Word, pk=word_id)

        correct_translation = ""

        for synonym in word_to_translate.synonyms.all():
            if synonym.language == base_language:
                # Getting the correct answer
                if len(correct_translation) != 0:
                    correct_translation += ", "
                correct_translation += synonym.word_name

        return correct_translation == answer, correct_translation


class ConjugationGameAnswerSerializer(serializers.Serializer):
    word_id = serializers.IntegerField()
    tense = serializers.CharField()
    conjugation_1 = serializers.CharField(allow_blank=True)
    conjugation_2 = serializers.CharField(allow_blank=True)
    conjugation_3 = serializers.CharField(allow_blank=True)
    conjugation_4 = serializers.CharField(allow_blank=True)
    conjugation_5 = serializers.CharField(allow_blank=True)
    conjugation_6 = serializers.CharField(allow_blank=True)

    def save(self, **kwargs):
        word_id = self.validated_data.get("word_id")
        tense = self.validated_data.get("tense")
        conjugation_1 = self.validated_data.get("conjugation_1")
        conjugation_2 = self.validated_data.get("conjugation_2")
        conjugation_3 = self.validated_data.get("conjugation_3")
        conjugation_4 = self.validated_data.get("conjugation_4")
        conjugation_5 = self.validated_data.get("conjugation_5")
        conjugation_6 = self.validated_data.get("conjugation_6")

        verb = get_object_or_404(Word, category__category_name="verbs", pk=word_id)
        conjugation = get_object_or_404(Conjugation, word=verb, tense=tense)
        language = verb.language

        correct_answer = language.personal_pronoun_1 + " " + conjugation.conjugation_1 + "\n" + \
                         language.personal_pronoun_2 + " " + conjugation.conjugation_2 + "\n" + \
                         language.personal_pronoun_3 + " " + conjugation.conjugation_3 + "\n" + \
                         language.personal_pronoun_4 + " " + conjugation.conjugation_4 + "\n" + \
                         language.personal_pronoun_5 + " " + conjugation.conjugation_5 + "\n" + \
                         language.personal_pronoun_6 + " " + conjugation.conjugation_6 + "\n"
        is_correct_answer = conjugation_1 == conjugation.conjugation_1 \
                            and conjugation_2 == conjugation.conjugation_2 \
                            and conjugation_3 == conjugation.conjugation_3 \
                            and conjugation_4 == conjugation.conjugation_4 \
                            and conjugation_5 == conjugation.conjugation_5 \
                            and conjugation_6 == conjugation.conjugation_6

        return is_correct_answer, correct_answer
