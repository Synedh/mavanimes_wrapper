# Generated by Django 4.1.4 on 2022-12-16 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('animes', '0002_anime_update_date_anime_versions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anime',
            name='name',
            field=models.CharField(max_length=1024, unique=True),
        ),
    ]
