# Generated by Django 5.0.6 on 2024-05-30 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movieapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watchedmovie',
            name='watched_at',
            field=models.DateField(blank=True),
        ),
    ]
