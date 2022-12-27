# Generated by Django 4.1.4 on 2022-12-27 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('animes', '0011_alter_tag_options_alter_episode_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='episode',
            name='type',
            field=models.CharField(blank=True, choices=[('EPISODE', 'Episode'), ('FILM', 'Film'), ('OAV', 'Oav'), ('SPECIAL', 'Special')], default='EPISODE', max_length=7, null=True),
        ),
    ]
