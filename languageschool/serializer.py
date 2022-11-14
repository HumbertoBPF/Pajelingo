from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from languageschool.models import Article, Category, Conjugation, Language, Meaning, Score, Word, Game
from languageschool.validation import is_valid_user_data


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'


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

    class Meta:
        model = Word
        exclude = ('image',)


class MeaningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meaning
        fields = '__all__'


class ConjugationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conjugation
        fields = '__all__'


class ListScoreSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    language = serializers.ReadOnlyField(source='language.language_name')
    game = serializers.ReadOnlyField(source='game.id')

    class Meta:
        model = Score
        fields = '__all__'


class UserSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.CharField()
    password = serializers.CharField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        username = validated_data.get("username")
        email = validated_data.get("email")
        password = validated_data.get("password")
        is_valid, error_message = is_valid_user_data(email, username, password, password)
        if not is_valid:
            raise ValidationError({"message": error_message})
        return User.objects.create_user(email=email, username=username, password=password)


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
