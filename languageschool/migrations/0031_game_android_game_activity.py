# Generated by Django 4.0.4 on 2022-11-14 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('languageschool', '0030_remove_game_game_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='android_game_activity',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
