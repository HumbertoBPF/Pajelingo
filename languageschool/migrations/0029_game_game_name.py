# Generated by Django 4.0.4 on 2022-06-13 03:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('languageschool', '0028_rename_game_name_game_game_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='game_name',
            field=models.CharField(blank=True, max_length=30, null=True, unique=True),
        ),
    ]
