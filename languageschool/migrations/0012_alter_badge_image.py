# Generated by Django 4.2.1 on 2023-06-03 19:13

from django.db import migrations, models
import languageschool.models


class Migration(migrations.Migration):

    dependencies = [
        ('languageschool', '0011_badge_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='badge',
            name='image',
            field=models.ImageField(upload_to=languageschool.models.get_upload_to),
        ),
    ]
