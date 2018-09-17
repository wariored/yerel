# Generated by Django 2.1.1 on 2018-09-16 19:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ads', '0005_auto_20180914_1237'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30)),
                ('price', models.FloatField(max_length=30)),
                ('condition', models.CharField(blank=True, choices=[('N', 'New'), ('U', 'Used')], max_length=1)),
                ('description', models.TextField(max_length=1000)),
                ('creation_date', models.DateTimeField(verbose_name='date created')),
                ('update_date', models.DateTimeField(auto_now_add=True, verbose_name='date updated')),
            ],
        ),
        migrations.CreateModel(
            name='AdFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media', models.FileField(upload_to='media/')),
            ],
        ),
        migrations.CreateModel(
            name='AdUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('phone_number', models.IntegerField()),
                ('email', models.EmailField(max_length=254)),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_ad_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.AlterField(
            model_name='subcategory',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='categ_subcategs', to='ads.Category'),
        ),
        migrations.AddField(
            model_name='adfile',
            name='ad',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='files', to='ads.Subcategory'),
        ),
        migrations.AddField(
            model_name='ad',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='loc_ads', to='ads.Location'),
        ),
        migrations.AddField(
            model_name='ad',
            name='subcategory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='subcateg_ads', to='ads.Subcategory'),
        ),
    ]
