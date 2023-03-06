# Generated by Django 4.1.4 on 2023-02-20 15:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('animes', '0022_alter_episode_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnimeImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.URLField(blank=True, default=None, null=True)),
                ('small_image', models.URLField(blank=True, default=None, null=True)),
                ('key', models.CharField(blank=True, default=None, max_length=128, null=True)),
                ('anime', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='animes.anime')),
            ],
        ),
        migrations.AddConstraint(
            model_name='animeimage',
            constraint=models.UniqueConstraint(fields=('anime', 'key'), name='unique_anime_key'),
        ),
    ]