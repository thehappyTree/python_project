# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-27 06:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hoapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='branch',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='hoapp.Branch', verbose_name='u_bpk'),
        ),
    ]
