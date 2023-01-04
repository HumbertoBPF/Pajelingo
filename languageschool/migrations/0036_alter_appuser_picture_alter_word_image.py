# Generated by Django 4.0.4 on 2023-01-02 19:11

from django.db import migrations, models
import languageschool.models


class Migration(migrations.Migration):

    dependencies = [
        ('languageschool', '0035_alter_language_flag_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appuser',
            name='picture',
            field=models.ImageField(blank=True, upload_to=languageschool.models.get_upload_to),
        ),
        migrations.AlterField(
            model_name='word',
            name='image',
            field=models.ImageField(blank=True, upload_to=languageschool.models.get_upload_to),
        ),
    ]
