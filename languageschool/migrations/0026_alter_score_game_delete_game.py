# Generated by Django 4.0.4 on 2022-06-12 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('languageschool', '0025_alter_score_game'),
    ]

    operations = [
        migrations.AlterField(
            model_name='score',
            name='game',
            field=models.CharField(max_length=30),
        ),
        migrations.DeleteModel(
            name='Game',
        ),
    ]