# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-03 02:48
from __future__ import unicode_literals

from django.db import migrations, models
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0005_auto_20170302_0128'),
    ]

    operations = [
        migrations.CreateModel(
            name='Accuracy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('model_type', models.TextField()),
                ('score', models.DecimalField(decimal_places=5, max_digits=5)),
            ],
        ),
        migrations.CreateModel(
            name='ModelStorage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vectorizer', picklefield.fields.PickledObjectField(editable=False)),
                ('classifier', picklefield.fields.PickledObjectField(editable=False)),
                ('vectorizer_needed', models.TextField(null=True)),
            ],
        ),
    ]