# Generated by Django 2.1.1 on 2018-09-18 11:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0011_auto_20180918_1128'),
    ]

    operations = [
        migrations.AddField(
            model_name='ad',
            name='ad_user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='ads', to='ads.AdUser'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='adfile',
            name='ad',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='ads.Ad'),
        ),
        migrations.AlterField(
            model_name='adfile',
            name='media',
            field=models.FileField(upload_to='ads_files/'),
        ),
        migrations.AlterField(
            model_name='category',
            name='icon',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]