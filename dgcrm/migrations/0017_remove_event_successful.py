# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-02 15:57
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dgcrm', '0016_auto_20170702_1544'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='successful',
        ),
    ]
