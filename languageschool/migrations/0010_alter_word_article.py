# Generated by Django 4.0.4 on 2022-04-27 14:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('languageschool', '0009_alter_word_article'),
    ]

    operations = [
        migrations.AlterField(
            model_name='word',
            name='article',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='languageschool.article'),
        ),
    ]
