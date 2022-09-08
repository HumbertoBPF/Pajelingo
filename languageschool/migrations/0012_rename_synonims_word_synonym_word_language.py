# Generated by Django 4.0.4 on 2022-04-28 01:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('languageschool', '0011_rename_article_article_article_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='word',
            old_name='synonims',
            new_name='synonym',
        ),
        migrations.AddField(
            model_name='word',
            name='language',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='languageschool.language'),
        ),
    ]
