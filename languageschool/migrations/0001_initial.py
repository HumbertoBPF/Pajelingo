# Generated by Django 4.0.4 on 2022-04-26 16:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('article', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('languague_name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=30)),
                ('category', models.CharField(blank=True, max_length=30)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='languageschool.article')),
                ('synonims', models.ManyToManyField(blank=True, to='languageschool.word')),
            ],
        ),
        migrations.CreateModel(
            name='Meaning',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meaning', models.TextField()),
                ('word', models.ManyToManyField(to='languageschool.word')),
            ],
        ),
        migrations.CreateModel(
            name='Conjugation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('conjugation_1', models.CharField(max_length=30)),
                ('conjugation_2', models.CharField(max_length=30)),
                ('conjugation_3', models.CharField(max_length=30)),
                ('conjugation_4', models.CharField(max_length=30)),
                ('conjugation_5', models.CharField(max_length=30)),
                ('conjugation_6', models.CharField(max_length=30)),
                ('tense', models.CharField(max_length=30)),
                ('word', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='languageschool.word')),
            ],
        ),
        migrations.AddField(
            model_name='article',
            name='language',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='languageschool.language'),
        ),
    ]
