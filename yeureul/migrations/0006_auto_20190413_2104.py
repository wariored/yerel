# Generated by Django 2.1.4 on 2019-04-13 21:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yeureul', '0005_historicalcontactmessage_historicaluserinfo_historicaluserkey'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicaluserkey',
            name='token',
            field=models.CharField(db_index=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='userkey',
            name='token',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
