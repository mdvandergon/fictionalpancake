# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-25 17:03
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0002_auto_20170224_2205'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='comment_id',
            new_name='api_comment_id',
        ),
        migrations.AlterUniqueTogether(
            name='comment',
            unique_together=set([('api_comment_id', 'outlet')]),
        ),
    ]
