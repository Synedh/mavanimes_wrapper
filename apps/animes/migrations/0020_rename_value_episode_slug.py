# Generated by Django 4.1.4 on 2023-02-04 10:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animes', '0019_alter_episode_options_anime_episodes_count'),
    ]

    operations = [
        migrations.RenameField(
            model_name='episode',
            old_name='value',
            new_name='slug',
        ),
    ]