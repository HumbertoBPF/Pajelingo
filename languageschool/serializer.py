from django.shortcuts import get_object_or_404
from languageschool.models import Article, Category, Conjugation, Language, Meaning, Score, Word, Game
from rest_framework import serializers


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
        exclude = ('image', )

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
    game = serializers.ReadOnlyField(source='game.game_tag')
    class Meta:
        model = Score
        fields = '__all__'

class ScoreSerializer(serializers.Serializer):
    language = serializers.CharField()
    game = serializers.CharField()

    def create(self, validated_data):
        language = get_object_or_404(Language, language_name = validated_data.get("language"))
        game = get_object_or_404(Game, game_tag = validated_data.get("game"))
        score = Score(user = self.context.get("user"), language = language, game = game, score = 1)
        score.save()
        return score

    def update(self, instance, validated_data):
        instance.score += 1
        instance.save()
        return instance