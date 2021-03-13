# Generated by Django 3.1.6 on 2021-03-13 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pastvina', '0005_auto_20210313_1114'),
    ]

    operations = [
        migrations.AddField(
            model_name='round',
            name='is_test',
            field=models.BooleanField(blank=True, default=False, verbose_name='testovací'),
        ),
        migrations.AddField(
            model_name='round',
            name='reload_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='obnovení dat'),
        ),
        migrations.AlterField(
            model_name='livestock',
            name='consumption',
            field=models.IntegerField(verbose_name='spotřeba'),
        ),
    ]