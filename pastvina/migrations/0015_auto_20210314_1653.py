# Generated by Django 3.1.6 on 2021-03-14 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pastvina', '0014_auto_20210314_1649'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='cropmarkethistory',
            index=models.Index(fields=['tick', 'crop'], name='pastvina_cr_tick_id_8f7542_idx'),
        ),
        migrations.AddIndex(
            model_name='livestockmarkethistory',
            index=models.Index(fields=['tick', 'livestock'], name='pastvina_li_tick_id_aba9c9_idx'),
        ),
        migrations.AddIndex(
            model_name='teamcropactionhistory',
            index=models.Index(fields=['tick', 'user', 'crop'], name='pastvina_te_tick_id_87a6ed_idx'),
        ),
        migrations.AddIndex(
            model_name='teamcrophistory',
            index=models.Index(fields=['tick', 'user', 'crop'], name='pastvina_te_tick_id_e3308d_idx'),
        ),
        migrations.AddIndex(
            model_name='teamhistory',
            index=models.Index(fields=['tick', 'user'], name='pastvina_te_tick_id_412ca5_idx'),
        ),
        migrations.AddIndex(
            model_name='teamlivestockactionhistory',
            index=models.Index(fields=['tick', 'user', 'livestock'], name='pastvina_te_tick_id_4ce3f9_idx'),
        ),
        migrations.AddIndex(
            model_name='teamlivestockhistory',
            index=models.Index(fields=['tick', 'user', 'livestock'], name='pastvina_te_tick_id_fe5ca8_idx'),
        ),
    ]
