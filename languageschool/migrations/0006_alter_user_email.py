# Generated by Django 4.2.1 on 2023-05-26 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('languageschool', '0005_alter_user_bio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='email address'),
        ),
    ]
