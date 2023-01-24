# Generated by Django 4.1.4 on 2023-01-05 21:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animes', '0015_alter_episode_pub_date_alter_episode_saison'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='episode',
            options={'ordering': ['number', 'season', 'version', 'anime__name'], 'verbose_name': 'Episode', 'verbose_name_plural': 'Episodes'},
        ),
        migrations.RenameField(
            model_name='episode',
            old_name='saison',
            new_name='season',
        ),
    ]