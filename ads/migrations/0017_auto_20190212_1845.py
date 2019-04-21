# Generated by Django 2.1.4 on 2019-02-12 18:45

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ads', '0016_historicalad_historicaladfile_historicaladuser_historicalcategory_historicallocation'),
    ]

    operations = [
        migrations.AddField(
            model_name='ad',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='ad',
            name='likes',
            field=models.ManyToManyField(blank=True, related_name='post_likes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='ad',
            name='views_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='historicalad',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicalad',
            name='views_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='ad',
            name='creation_date',
            field=models.DateTimeField(verbose_name='da    te created'),
        ),
        migrations.AlterField(
            model_name='historicalad',
            name='creation_date',
            field=models.DateTimeField(verbose_name='da    te created'),
        ),
    ]
