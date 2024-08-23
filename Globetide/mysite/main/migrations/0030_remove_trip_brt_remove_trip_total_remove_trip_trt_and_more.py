# Generated by Django 4.2.6 on 2024-07-23 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0029_trip_total'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trip',
            name='brt',
        ),
        migrations.RemoveField(
            model_name='trip',
            name='total',
        ),
        migrations.RemoveField(
            model_name='trip',
            name='trt',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='brt',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='total',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='trt',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
