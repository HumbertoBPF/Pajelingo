# Generated by Django 4.0.4 on 2022-06-13 03:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('languageschool', '0027_game_alter_score_game'),
    ]

    operations = [
        migrations.RenameField(
            model_name='game',
            old_name='game_name',
            new_name='game_tag',
        ),
    ]
