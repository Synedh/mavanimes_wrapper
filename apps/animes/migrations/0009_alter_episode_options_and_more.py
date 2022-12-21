# Generated by Django 4.1.4 on 2022-12-21 15:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animes', '0008_videourl_source_alter_episode_anime'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='episode',
            options={'ordering': ['number', 'saison', 'version', 'anime__name'], 'verbose_name': 'Episode', 'verbose_name_plural': 'Episodes'},
        ),
        migrations.RenameField(
            model_name='episode',
            old_name='upload_date',
            new_name='pub_date',
        ),
        migrations.RemoveField(
            model_name='episode',
            name='image',
        ),
        migrations.RemoveField(
            model_name='episode',
            name='small_image',
        ),
    ]
