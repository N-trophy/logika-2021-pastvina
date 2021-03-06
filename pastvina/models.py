from colorfield.fields import ColorField
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.db.models import Q
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from os import path, rename


class Contribution(models.Model):
    class Meta:
        verbose_name = 'novinka'
        verbose_name_plural = 'novinky'

    name = models.CharField('název', max_length=60)
    text = models.TextField('text novinky')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='autor')
    published = models.BooleanField('publikováno', default=False, blank=True)
    public_from = models.DateTimeField('publikováno od', null=True, blank=True)


class Round(models.Model):
    """
    Contains data relate to <game> at the <beginning of round>.
    """
    class Meta:
        verbose_name = 'kolo'
        verbose_name_plural = 'kola'

    id = models.AutoField(primary_key=True)
    start = models.DateTimeField('start')
    ticks = models.IntegerField('počet minikol')
    period = models.TimeField('délka minikola')

    crop_storage_size = models.IntegerField('velikost skladu')
    livestock_slaughter_limit = models.IntegerField('limit porážení')

    start_money = models.PositiveIntegerField('počáteční peníze')


class Crop(models.Model):
    """
    Contains data related to <crop> through the <whole game>.
    """
    class Meta:
        verbose_name = 'plodina'
        verbose_name_plural = 'plodiny'

    name = models.CharField('jméno', max_length=30)
    name_genitive = models.CharField('jméno (druhý pád)', max_length=30)

    base_price_buy = models.IntegerField('základní nákupní cena')
    base_price_sell = models.IntegerField('základní prodejní cena')

    growth_time = models.IntegerField('čas růstu')
    rotting_time = models.IntegerField('čas kažení')

    color = ColorField(verbose_name='barva', default='#aaaaaa', format='hexa')


class Livestock(models.Model):
    """
    Contains data related to <livestock> through the <whole game>.
    """
    class Meta:
        verbose_name = 'dobytek'
        verbose_name_plural = 'dobytek'

    name = models.CharField('jméno', max_length=30)
    name_genitive = models.CharField('jméno (druhý pád)', max_length=30)

    base_price_buy = models.IntegerField('základní nákupní cena')
    base_price_sell = models.IntegerField('základní prodejní cena')

    product_name = models.CharField('jméno produktu', max_length=30, null=True, blank=True)
    product_name_genitive = models.CharField('jméno produktu (druhý pád)', max_length=30, null=True, blank=True)
    product_price = models.IntegerField('základní cena produktu')

    growth_time = models.IntegerField('čas růstu')
    life_time = models.IntegerField('čas života')

    consumption = models.FloatField("spotřeba")
    consumption_type = models.ForeignKey(Crop, on_delete=models.RESTRICT, null=False, verbose_name='krmivo')

    color = ColorField(verbose_name='barva', default='#aaaaaa', format='hexa')


class TeamCropHistory(models.Model):
    class Meta:
        verbose_name = 'historie herních parametrů týmu (plodiny)'
        verbose_name_plural = 'historie herních parametrů týmů (plodiny)'
        unique_together = (('round', 'user', 'tick', 'crop', 'age'),)

    round = models.ForeignKey(Round, on_delete=models.RESTRICT, null=False, verbose_name='kolo')
    user = models.ForeignKey(User, on_delete=models.RESTRICT, null=False, verbose_name='tým')
    tick = models.PositiveIntegerField('číslo minikola')
    crop = models.ForeignKey(Crop, on_delete=models.RESTRICT, null=False, verbose_name='plodina')
    age = models.IntegerField('stáří produktu')

    amount = models.IntegerField('množství')


class TeamLivestockHistory(models.Model):
    class Meta:
        verbose_name = 'historie herních parametrů týmu (dobytek)'
        verbose_name_plural = 'historie herních parametrů týmů (dobytek)'
        unique_together = (('round', 'user', 'tick', 'livestock', 'age'),)

    round = models.ForeignKey(Round, on_delete=models.RESTRICT, null=False, verbose_name='kolo')
    user = models.ForeignKey(User, on_delete=models.RESTRICT, null=False, verbose_name='tým')
    tick = models.PositiveIntegerField('číslo minikola')
    livestock = models.ForeignKey(Crop, on_delete=models.RESTRICT, null=False, verbose_name='dobytek')
    age = models.IntegerField('stáří dobytka')

    amount = models.IntegerField('množství')


class TeamHistory(models.Model):
    """
    Contains data related to the <team> at <each tick> of <each round>
    """

    class Meta:
        verbose_name = 'historie herních parametrů týmu'
        verbose_name_plural = 'historie herních parametrů týmů'
        unique_together = (('round', 'user', 'tick'),)

    round = models.ForeignKey(Round, on_delete=models.RESTRICT, null=False, verbose_name='kolo')
    user = models.ForeignKey(User, on_delete=models.RESTRICT, null=False, verbose_name='tým')
    tick = models.PositiveIntegerField('číslo minikola')

    money = models.IntegerField('peníze')


class CropMarketHistory(models.Model):
    """
    Contains data related to the <crop> market at <each tick> of <each round>
    """
    class Meta:
        verbose_name = 'historie obchodu (plodiny)'
        verbose_name_plural = 'historie obchodů (plodiny)'
        unique_together = (('round', 'tick', 'crop'),)

    round = models.ForeignKey(Round, on_delete=models.RESTRICT, null=False, verbose_name='kolo')
    tick = models.PositiveIntegerField('číslo minikola')
    crop = models.ForeignKey(Crop, on_delete=models.RESTRICT, null=False, verbose_name='plodina')

    amount_sold = models.PositiveIntegerField('prodané množství')
    current_price_buy = models.PositiveIntegerField('nákupní cena')
    current_price_sell = models.PositiveIntegerField('prodejní cena')


class LivestockMarketHistory(models.Model):
    """
    Contains data related to the <livestock> market at <each tick> of <each round>
    """
    class Meta:
        verbose_name = 'historie obchodu (dobytek)'
        verbose_name_plural = 'hisotire obchodů (dobytek)'
        unique_together = (('round', 'tick', 'livestock'),)

    round = models.ForeignKey(Round, on_delete=models.RESTRICT, null=False, verbose_name='kolo')
    tick = models.PositiveIntegerField('číslo minikola')
    livestock = models.ForeignKey(Livestock, on_delete=models.RESTRICT, null=False, verbose_name='dobytek')

    amount_sold = models.PositiveIntegerField('prodané množství')
    current_price_buy = models.PositiveIntegerField('nákupní cena')
    current_price_sell = models.PositiveIntegerField('prodejní cena')

    product_amount_sold = models.PositiveIntegerField('prodané množství')
    product_current_price = models.PositiveIntegerField('aktuální cena')
