# Generated by Django 4.1.4 on 2022-12-16 12:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animes', '0003_alter_anime_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='videourl',
            options={'ordering': ['-episode__id'], 'verbose_name': 'Video URL', 'verbose_name_plural': 'Video URLs'},
        ),
    ]
