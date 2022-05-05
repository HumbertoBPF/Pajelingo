from django.db import models

# Create your models here.
class Language(models.Model):
    language_name = models.CharField(max_length=30)
    personal_pronoun_1 = models.CharField(max_length=30, blank=True, null=True)
    personal_pronoun_2 = models.CharField(max_length=30, blank=True, null=True)
    personal_pronoun_3 = models.CharField(max_length=30, blank=True, null=True)
    personal_pronoun_4 = models.CharField(max_length=30, blank=True, null=True)
    personal_pronoun_5 = models.CharField(max_length=30, blank=True, null=True)
    personal_pronoun_6 = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return self.language_name

class Category(models.Model):
    category_name = models.CharField(max_length=30)

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
    synonym = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return  ((str(self.article.article_name) + " ") if (self.article != None) else "") + self.word_name

class Meaning(models.Model):
    word = models.ManyToManyField(Word)
    meaning = models.TextField()

    def __str__(self):
        return self.word

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