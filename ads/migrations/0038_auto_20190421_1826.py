# Generated by Django 2.1.4 on 2019-04-21 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0037_auto_20190420_1812'),
    ]

    operations = [
        migrations.AddField(
            model_name='ad',
            name='signal',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='historicalad',
            name='signal',
            field=models.IntegerField(default=0),
        ),
    ]