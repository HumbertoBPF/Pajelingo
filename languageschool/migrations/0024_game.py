# Generated by Django 4.0.4 on 2022-06-12 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('languageschool', '0023_alter_category_category_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_name', models.CharField(blank=True, max_length=30, null=True, unique=True)),
            ],
        ),
    ]