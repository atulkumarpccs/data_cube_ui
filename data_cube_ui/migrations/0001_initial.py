# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-14 17:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AnimationType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_id', models.CharField(default='None', max_length=25)),
                ('type_name', models.CharField(default='None', max_length=25)),
                ('data_variable', models.CharField(default='None', max_length=25)),
                ('band_number', models.CharField(default='None', max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area_id', models.CharField(default='', max_length=250)),
                ('area_name', models.CharField(default='', max_length=250)),
                ('area_product', models.CharField(default='', max_length=250)),
                ('latitude_min', models.FloatField(default=0)),
                ('latitude_max', models.FloatField(default=0)),
                ('longitude_min', models.FloatField(default=0)),
                ('longitude_max', models.FloatField(default=0)),
                ('date_min', models.DateField(verbose_name='date_min')),
                ('date_max', models.DateField(verbose_name='date_min')),
                ('main_imagery', models.CharField(default='', max_length=250)),
                ('detail_imagery', models.CharField(default='', max_length=250)),
                ('detail_latitude_min', models.FloatField(default=0)),
                ('detail_latitude_max', models.FloatField(default=0)),
                ('detail_longitude_min', models.FloatField(default=0)),
                ('detail_longitude_max', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Compositor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('compositor', models.CharField(max_length=25)),
                ('compositor_id', models.CharField(max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name='Satellite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('satellite_id', models.CharField(max_length=25)),
                ('satellite_name', models.CharField(max_length=25)),
            ],
        ),
    ]