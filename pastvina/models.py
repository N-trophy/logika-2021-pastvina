from colorfield.fields import ColorField
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.db.models import Q
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from os import path, rename
from datetime import datetime, timedelta
from django.utils import timezone


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
    reload_time = models.DateTimeField('obnovení dat', null=True, blank=True)
    is_test = models.BooleanField('testovací', default=False, blank=True)
    ticks = models.IntegerField('počet minikol')
    period = models.IntegerField('délka minikola v 10s')

    crop_storage_size = models.IntegerField('velikost skladu')
    livestock_slaughter_limit = models.IntegerField('limit porážení')

    start_money = models.PositiveIntegerField('počáteční peníze')

    def __repr__(self) -> str:
        return f'kolo {self.id}: Start {self.start}'

    __str__ = __repr__

    def last_tick_time(self) -> datetime:
        """Time of last tick which should happen"""
        return self.start + timedelta(seconds=self.ticks * self.period * 10)

    def is_running(self) -> bool:
        return self.start <= timezone.now() <= self.last_tick_time()

    # def current_tick(self) -> int:
    #     return int((datetime.now()-self.start).total_seconds() + 1) // (10 * self.period)


class Tick(models.Model):
    """Tick is associated to round"""
    class Meta:
        verbose_name = 'tick'
        verbose_name_plural = 'ticky'
        unique_together = (('round', 'index'),)

    id = models.AutoField(primary_key=True)
    index = models.IntegerField('index')
    round = models.ForeignKey(Round, on_delete=models.RESTRICT, null=False, verbose_name='kolo')

    # Just helpers
    start = models.DateTimeField('start')

    def __str__(self):
        return "tick {0} ({1})".format(self.index, self.round)


class Crop(models.Model):
    """
    Contains data related to <crop> through the <whole game>.
    """
    class Meta:
        verbose_name = 'plodina'
        verbose_name_plural = 'plodiny'

    id = models.AutoField(primary_key=True)
    name = models.CharField('jméno', max_length=30)
    name_genitive = models.CharField('jméno (druhý pád)', max_length=30)

    base_price_buy = models.IntegerField('základní nákupní cena')
    base_price_sell = models.IntegerField('základní prodejní cena')

    growth_time = models.IntegerField('čas růstu')
    rotting_time = models.IntegerField('čas kažení')

    color = ColorField(verbose_name='barva', default='#aaaaaa', format='hexa')

    def __repr__(self) -> str:
        return f'{self.id}: {self.name}'

    __str__ = __repr__


class Livestock(models.Model):
    """
    Contains data related to <livestock> through the <whole game>.
    """
    class Meta:
        verbose_name = 'dobytek'
        verbose_name_plural = 'dobytek'

    id = models.AutoField(primary_key=True)
    name = models.CharField('jméno', max_length=30)
    name_genitive = models.CharField('jméno (druhý pád)', max_length=30)

    base_price_buy = models.IntegerField('základní nákupní cena')
    base_price_sell = models.IntegerField('základní prodejní cena')

    product_name = models.CharField('jméno produktu', max_length=30, null=True, blank=True)
    product_name_genitive = models.CharField('jméno produktu (druhý pád)', max_length=30, null=True, blank=True)
    product_price = models.IntegerField('základní cena produktu')

    growth_time = models.IntegerField('čas růstu')
    life_time = models.IntegerField('čas života')

    consumption = models.IntegerField("spotřeba")
    consumption_type = models.ForeignKey(Crop, on_delete=models.RESTRICT, null=False, verbose_name='krmivo')

    color = ColorField(verbose_name='barva', default='#aaaaaa', format='hexa')

    def __repr__(self) -> str:
        return f'{self.id}: {self.name}'

    __str__ = __repr__


class TeamCropHistory(models.Model):
    class Meta:
        verbose_name = 'historie herních parametrů týmu (plodiny)'
        verbose_name_plural = 'historie herních parametrů týmů (plodiny)'
        unique_together = (('tick', 'user', 'crop', 'age'),)

    id = models.AutoField(primary_key=True)
    tick = models.ForeignKey(Tick, on_delete=models.CASCADE, verbose_name='minikolo')
    user = models.ForeignKey(User, on_delete=models.RESTRICT, null=False, verbose_name='tým')
    crop = models.ForeignKey(Crop, on_delete=models.RESTRICT, null=False, verbose_name='plodina')
    age = models.IntegerField('čas do zkažení produktu')

    amount = models.IntegerField('množství')


class TeamLivestockHistory(models.Model):
    class Meta:
        verbose_name = 'historie herních parametrů týmu (dobytek)'
        verbose_name_plural = 'historie herních parametrů týmů (dobytek)'
        unique_together = (('tick', 'user', 'livestock', 'age'),)

    id = models.AutoField(primary_key=True)
    tick = models.ForeignKey(Tick, on_delete=models.CASCADE, verbose_name='minikolo')
    user = models.ForeignKey(User, on_delete=models.RESTRICT, null=False, verbose_name='tým')
    livestock = models.ForeignKey(Livestock, on_delete=models.RESTRICT, null=False, verbose_name='dobytek')
    age = models.IntegerField('čas do smrti dobytka')

    amount = models.IntegerField('množství', default=0)


class TeamHistory(models.Model):
    """
    Contains data related to the <team> at <each tick> of <each round>
    """

    class Meta:
        verbose_name = 'historie herních parametrů týmu'
        verbose_name_plural = 'historie herních parametrů týmů'
        unique_together = (('tick', 'user'),)

    id = models.AutoField(primary_key=True)
    tick = models.ForeignKey(Tick, on_delete=models.CASCADE, verbose_name='minikolo')
    user = models.ForeignKey(User, on_delete=models.RESTRICT, null=False, verbose_name='tým')

    slaughtered = models.PositiveIntegerField('prodáno zvířat', default=0)
    money = models.IntegerField('peníze')


class CropMarketHistory(models.Model):
    """
    Contains data related to the <crop> market at <each tick> of <each round>
    """
    class Meta:
        verbose_name = 'historie obchodu (plodiny)'
        verbose_name_plural = 'historie obchodů (plodiny)'
        unique_together = (('tick', 'crop'),)

    id = models.AutoField(primary_key=True)
    tick = models.ForeignKey(Tick, on_delete=models.CASCADE, verbose_name='minikolo')
    crop = models.ForeignKey(Crop, on_delete=models.RESTRICT, null=False, verbose_name='plodina')

    amount_sold = models.IntegerField('prodané množství')
    current_price_buy = models.PositiveIntegerField('nákupní cena')
    current_price_sell = models.PositiveIntegerField('prodejní cena')


class LivestockMarketHistory(models.Model):
    """
    Contains data related to the <livestock> market at <each tick> of <each round>
    """
    class Meta:
        verbose_name = 'historie obchodu (dobytek)'
        verbose_name_plural = 'historie obchodů (dobytek)'
        unique_together = (('tick', 'livestock'),)

    id = models.AutoField(primary_key=True)
    tick = models.ForeignKey(Tick, on_delete=models.CASCADE, verbose_name='minikolo')
    livestock = models.ForeignKey(Livestock, on_delete=models.RESTRICT, null=False, verbose_name='dobytek')

    amount_sold = models.IntegerField('prodané množství zvířete')
    current_price_buy = models.PositiveIntegerField('nákupní cena zvířete')
    current_price_sell = models.PositiveIntegerField('prodejní cena zvířete')

    product_amount_sold = models.IntegerField('prodané množství produktu')
    product_current_price = models.PositiveIntegerField('aktuální cena produktu')
