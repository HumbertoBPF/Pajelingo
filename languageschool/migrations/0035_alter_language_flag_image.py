# Generated by Django 4.0.4 on 2023-01-02 19:09

from django.db import migrations, models
import languageschool.models


class Migration(migrations.Migration):

    dependencies = [
        ('languageschool', '0034_language_flag_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='language',
            name='flag_image',
            field=models.ImageField(blank=True, upload_to=languageschool.models.get_upload_to),
        ),
    ]
