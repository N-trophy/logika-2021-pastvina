# Generated by Django 3.1.6 on 2021-03-17 11:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pastvina', '0016_auto_20210314_2227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cropmarkethistory',
            name='crop',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='states', to='pastvina.crop', verbose_name='plodina'),
        ),
        migrations.AlterField(
            model_name='cropmarkethistory',
            name='tick',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='crop_states', to='pastvina.tick', verbose_name='minikolo'),
        ),
        migrations.AlterField(
            model_name='livestockmarkethistory',
            name='livestock',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='states', to='pastvina.livestock', verbose_name='dobytek'),
        ),
        migrations.AlterField(
            model_name='livestockmarkethistory',
            name='tick',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='livestock_states', to='pastvina.tick', verbose_name='minikolo'),
        ),
        migrations.AlterField(
            model_name='tick',
            name='round',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='all_ticks', to='pastvina.round', verbose_name='kolo'),
        ),
    ]