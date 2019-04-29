# Generated by Django 2.1.4 on 2019-01-25 18:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import pricing.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Pricing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('N', 'NORMAL'), ('A', 'ADVANCED'), ('P', 'PROFESSIONAL')], max_length=1)),
                ('active_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('end_date', models.DateTimeField(default=pricing.models.one_month_hence)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='pricing', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PricingHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('token', models.CharField(max_length=255)),
                ('amount', models.IntegerField()),
                ('pricing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='histories', to='pricing.Pricing')),
            ],
        ),
    ]