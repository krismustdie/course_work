# Generated by Django 5.0.6 on 2024-05-30 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movieapp', '0002_alter_watchedmovie_watched_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watchedmovie',
            name='watched_at',
            field=models.DateField(default=None),
        ),
    ]
