# Generated by Django 2.1.4 on 2019-03-01 22:29

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0026_auto_20190301_2154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adfeatured',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2019, 3, 3, 22, 29, 51, 790211, tzinfo=utc), verbose_name='end date'),
        ),
        migrations.AlterField(
            model_name='historicaladfeatured',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2019, 3, 3, 22, 29, 51, 790211, tzinfo=utc), verbose_name='end date'),
        ),
    ]