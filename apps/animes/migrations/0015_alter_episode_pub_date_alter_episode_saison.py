# Generated by Django 4.1.4 on 2022-12-30 20:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('animes', '0014_alter_anime_description_alter_anime_mav_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='pub_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='episode',
            name='saison',
            field=models.IntegerField(blank=True, default=1),
        ),
    ]
