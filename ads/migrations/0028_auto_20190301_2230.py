# Generated by Django 2.1.4 on 2019-03-01 22:30

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0027_auto_20190301_2229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adfeatured',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2019, 3, 3, 22, 30, 7, 780536, tzinfo=utc), verbose_name='end date'),
        ),
        migrations.AlterField(
            model_name='historicaladfeatured',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2019, 3, 3, 22, 30, 7, 780536, tzinfo=utc), verbose_name='end date'),
        ),
    ]
