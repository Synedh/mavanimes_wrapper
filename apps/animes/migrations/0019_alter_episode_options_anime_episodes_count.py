# Generated by Django 4.1.4 on 2023-01-08 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('animes', '0018_alter_tag_color'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='episode',
            options={'ordering': ['season', 'number', 'version', 'anime__name'], 'verbose_name': 'Episode', 'verbose_name_plural': 'Episodes'},
        ),
        migrations.AddField(
            model_name='anime',
            name='episodes_count',
            field=models.IntegerField(default=0),
        ),
    ]