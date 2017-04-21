# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-02 01:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0004_auto_20170227_0528'),
    ]

    operations = [
        migrations.CreateModel(
            name='Progress',
            fields=[
                ('forum', models.TextField(primary_key=True, serialize=False)),
                ('progress', models.TextField()),
            ],
        ),
        migrations.AlterField(
            model_name='author',
            name='location',
            field=models.TextField(null=True),
        ),
    ]
