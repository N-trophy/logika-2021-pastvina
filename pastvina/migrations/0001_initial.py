# Generated by Django 3.1.6 on 2021-03-06 12:43

import colorfield.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Crop',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30, verbose_name='jméno')),
                ('name_genitive', models.CharField(max_length=30, verbose_name='jméno (druhý pád)')),
                ('base_price_buy', models.IntegerField(verbose_name='základní nákupní cena')),
                ('base_price_sell', models.IntegerField(verbose_name='základní prodejní cena')),
                ('growth_time', models.IntegerField(verbose_name='čas růstu')),
                ('rotting_time', models.IntegerField(verbose_name='čas kažení')),
                ('color', colorfield.fields.ColorField(default='#aaaaaa', max_length=18, verbose_name='barva')),
            ],
            options={
                'verbose_name': 'plodina',
                'verbose_name_plural': 'plodiny',
            },
        ),
        migrations.CreateModel(
            name='Livestock',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30, verbose_name='jméno')),
                ('name_genitive', models.CharField(max_length=30, verbose_name='jméno (druhý pád)')),
                ('base_price_buy', models.IntegerField(verbose_name='základní nákupní cena')),
                ('base_price_sell', models.IntegerField(verbose_name='základní prodejní cena')),
                ('product_name', models.CharField(blank=True, max_length=30, null=True, verbose_name='jméno produktu')),
                ('product_name_genitive', models.CharField(blank=True, max_length=30, null=True, verbose_name='jméno produktu (druhý pád)')),
                ('product_price', models.IntegerField(verbose_name='základní cena produktu')),
                ('growth_time', models.IntegerField(verbose_name='čas růstu')),
                ('life_time', models.IntegerField(verbose_name='čas života')),
                ('consumption', models.FloatField(verbose_name='spotřeba')),
                ('color', colorfield.fields.ColorField(default='#aaaaaa', max_length=18, verbose_name='barva')),
                ('consumption_type', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='pastvina.crop', verbose_name='krmivo')),
            ],
            options={
                'verbose_name': 'dobytek',
                'verbose_name_plural': 'dobytek',
            },
        ),
        migrations.CreateModel(
            name='Round',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('start', models.DateTimeField(verbose_name='start')),
                ('ticks', models.IntegerField(verbose_name='počet minikol')),
                ('period', models.TimeField(verbose_name='délka minikola')),
                ('crop_storage_size', models.IntegerField(verbose_name='velikost skladu')),
                ('livestock_slaughter_limit', models.IntegerField(verbose_name='limit porážení')),
                ('start_money', models.PositiveIntegerField(verbose_name='počáteční peníze')),
            ],
            options={
                'verbose_name': 'kolo',
                'verbose_name_plural': 'kola',
            },
        ),
        migrations.CreateModel(
            name='Tick',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('index', models.IntegerField(verbose_name='index')),
                ('start', models.DateTimeField(verbose_name='start')),
                ('round', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='pastvina.round', verbose_name='kolo')),
            ],
            options={
                'verbose_name': 'tick',
                'verbose_name_plural': 'ticky',
                'unique_together': {('round', 'index')},
            },
        ),
        migrations.CreateModel(
            name='Contribution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60, verbose_name='název')),
                ('text', models.TextField(verbose_name='text novinky')),
                ('published', models.BooleanField(blank=True, default=False, verbose_name='publikováno')),
                ('public_from', models.DateTimeField(blank=True, null=True, verbose_name='publikováno od')),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='autor')),
            ],
            options={
                'verbose_name': 'novinka',
                'verbose_name_plural': 'novinky',
            },
        ),
        migrations.CreateModel(
            name='TeamLivestockHistory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('age', models.IntegerField(verbose_name='stáří dobytka')),
                ('amount', models.IntegerField(verbose_name='množství')),
                ('livestock', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='pastvina.livestock', verbose_name='dobytek')),
                ('tick', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pastvina.tick', verbose_name='minikolo')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL, verbose_name='tým')),
            ],
            options={
                'verbose_name': 'historie herních parametrů týmu (dobytek)',
                'verbose_name_plural': 'historie herních parametrů týmů (dobytek)',
                'unique_together': {('tick', 'user', 'livestock', 'age')},
            },
        ),
        migrations.CreateModel(
            name='TeamHistory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('money', models.IntegerField(verbose_name='peníze')),
                ('tick', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pastvina.tick', verbose_name='minikolo')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL, verbose_name='tým')),
            ],
            options={
                'verbose_name': 'historie herních parametrů týmu',
                'verbose_name_plural': 'historie herních parametrů týmů',
                'unique_together': {('tick', 'user')},
            },
        ),
        migrations.CreateModel(
            name='TeamCropHistory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('age', models.IntegerField(verbose_name='stáří produktu')),
                ('amount', models.IntegerField(verbose_name='množství')),
                ('crop', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='pastvina.crop', verbose_name='plodina')),
                ('tick', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pastvina.tick', verbose_name='minikolo')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL, verbose_name='tým')),
            ],
            options={
                'verbose_name': 'historie herních parametrů týmu (plodiny)',
                'verbose_name_plural': 'historie herních parametrů týmů (plodiny)',
                'unique_together': {('tick', 'user', 'crop', 'age')},
            },
        ),
        migrations.CreateModel(
            name='LivestockMarketHistory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('amount_sold', models.PositiveIntegerField(verbose_name='prodané množství zvířete')),
                ('current_price_buy', models.PositiveIntegerField(verbose_name='nákupní cena zvířete')),
                ('current_price_sell', models.PositiveIntegerField(verbose_name='prodejní cena zvířete')),
                ('product_amount_sold', models.PositiveIntegerField(verbose_name='prodané množství produktu')),
                ('product_current_price', models.PositiveIntegerField(verbose_name='aktuální cena produktu')),
                ('livestock', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='pastvina.livestock', verbose_name='dobytek')),
                ('tick', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pastvina.tick', verbose_name='minikolo')),
            ],
            options={
                'verbose_name': 'historie obchodu (dobytek)',
                'verbose_name_plural': 'historie obchodů (dobytek)',
                'unique_together': {('tick', 'livestock')},
            },
        ),
        migrations.CreateModel(
            name='CropMarketHistory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('amount_sold', models.PositiveIntegerField(verbose_name='prodané množství')),
                ('current_price_buy', models.PositiveIntegerField(verbose_name='nákupní cena')),
                ('current_price_sell', models.PositiveIntegerField(verbose_name='prodejní cena')),
                ('crop', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='pastvina.crop', verbose_name='plodina')),
                ('tick', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pastvina.tick', verbose_name='minikolo')),
            ],
            options={
                'verbose_name': 'historie obchodu (plodiny)',
                'verbose_name_plural': 'historie obchodů (plodiny)',
                'unique_together': {('tick', 'crop')},
            },
        ),
    ]
