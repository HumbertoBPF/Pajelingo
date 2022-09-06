# Generated by Django 4.0.4 on 2022-06-12 15:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('languageschool', '0026_alter_score_game_delete_game'),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_name', models.CharField(blank=True, max_length=30, null=True, unique=True)),
            ],
        ),
        migrations.AlterField(
            model_name='score',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='languageschool.game'),
        ),
    ]