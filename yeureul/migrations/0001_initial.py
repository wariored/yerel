# Generated by Django 2.1.4 on 2019-05-10 10:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import yeureul.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('subject', models.CharField(blank=True, max_length=200, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('message', models.TextField(max_length=2000)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contact_messages', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.IntegerField(blank=True, null=True)),
                ('address', models.CharField(blank=True, max_length=200, null=True)),
                ('avatar', models.FileField(blank=True, null=True, upload_to=yeureul.models.get_file_path)),
                ('activated_account', models.BooleanField(default=False)),
                ('creation_date', models.DateTimeField(verbose_name='date created')),
                ('updated_date', models.DateTimeField(auto_now_add=True, verbose_name='date updated')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='info', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key_type', models.CharField(choices=[('P', 'PASSWORD'), ('A', 'ACTIVATION')], max_length=1)),
                ('token', models.CharField(max_length=100, unique=True)),
                ('key_expires', models.DateTimeField(default=yeureul.models.one_day_hence)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='keys', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
