# Generated by Django 4.0.4 on 2022-06-12 14:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('languageschool', '0024_game'),
    ]

    operations = [
        migrations.AlterField(
            model_name='score',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='languageschool.game'),
        ),
    ]
