# Generated by Django 3.1.6 on 2021-03-17 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pastvina', '0017_auto_20210317_1212'),
    ]

    operations = [
        migrations.AddField(
            model_name='round',
            name='name',
            field=models.CharField(default='test', max_length=60, verbose_name='název'),
            preserve_default=False,
        ),
    ]
