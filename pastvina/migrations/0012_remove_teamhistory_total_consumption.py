# Generated by Django 3.1.6 on 2021-03-14 15:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pastvina', '0011_auto_20210314_1304'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teamhistory',
            name='total_consumption',
        ),
    ]
