# Generated by Django 4.0.4 on 2022-04-27 14:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('languageschool', '0007_alter_word_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='word',
            name='article',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='languageschool.article'),
        ),
    ]
