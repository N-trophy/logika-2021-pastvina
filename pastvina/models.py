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
    public_from = models.DateTimeField('veřejné od', default=timezone.now, blank=True)


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
    ticks = models.PositiveIntegerField('počet minikol')
    period = models.PositiveIntegerField('délka minikola v 10s')

    crop_storage_size = models.PositiveIntegerField('velikost skladu')
    livestock_slaughter_limit = models.PositiveIntegerField('limit porážení')

    start_money = models.PositiveIntegerField('počáteční peníze')

    def __repr__(self) -> str:
        return f'kolo {self.id}: Start {self.start}'

    __str__ = __repr__

    def is_running(self) -> bool:
        if self.start > timezone.now():
            return False
        last_tick = Tick.objects.filter(round=self).order_by('index').last()
        if last_tick is None:
            return True
        return last_tick.index < self.ticks


class Tick(models.Model):
    """Tick is associated to round"""
    class Meta:
        verbose_name = 'tick'
        verbose_name_plural = 'ticky'
        unique_together = (('round', 'index'),)

    id = models.AutoField(primary_key=True)
    index = models.PositiveIntegerField('index')
    round = models.ForeignKey(Round, on_delete=models.RESTRICT, verbose_name='kolo')

    start = models.DateTimeField('start', default=timezone.now)

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

    growth_time = models.PositiveIntegerField('čas růstu')
    rotting_time = models.PositiveIntegerField('čas kažení')

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

    product_name = models.CharField('jméno produktu', max_length=30)
    product_name_genitive = models.CharField('jméno produktu (druhý pád)', max_length=30)
    product_price = models.IntegerField('základní cena produktu')

    growth_time = models.PositiveIntegerField('čas růstu')
    life_time = models.PositiveIntegerField('čas života')

    consumption = models.PositiveIntegerField("spotřeba")
    consumption_type = models.ForeignKey(Crop, on_delete=models.RESTRICT, verbose_name='krmivo')

    color = ColorField(verbose_name='barva', default='#aaaaaa', format='hexa')

    def __repr__(self) -> str:
        return f'{self.id}: {self.name}'

    __str__ = __repr__


class CropMarketHistory(models.Model):
    """
    Contains data related to the <crop> market at <each tick> of <each round>
    """
    class Meta:
        verbose_name = 'plodiny - historie obchodu'
        verbose_name_plural = 'plodiny - historie obchodů'
        unique_together = (('tick', 'crop'),)

    id = models.AutoField(primary_key=True)
    tick = models.ForeignKey(Tick, on_delete=models.CASCADE, verbose_name='minikolo')
    crop = models.ForeignKey(Crop, on_delete=models.RESTRICT, verbose_name='plodina')

    amount_sold = models.IntegerField('prodané množství', default=0)
    current_price_buy = models.PositiveIntegerField('nákupní cena')
    current_price_sell = models.PositiveIntegerField('prodejní cena')


class LivestockMarketHistory(models.Model):
    """
    Contains data related to the <livestock> market at <each tick> of <each round>
    """
    class Meta:
        verbose_name = 'dobytek - historie obchodu'
        verbose_name_plural = 'dobytek - historie obchodů'
        unique_together = (('tick', 'livestock'),)

    id = models.AutoField(primary_key=True)
    tick = models.ForeignKey(Tick, on_delete=models.CASCADE, verbose_name='minikolo')
    livestock = models.ForeignKey(Livestock, on_delete=models.RESTRICT, verbose_name='dobytek')

    amount_sold = models.IntegerField('prodané množství zvířete', default=0)
    current_price_buy = models.PositiveIntegerField('nákupní cena zvířete')
    current_price_sell = models.PositiveIntegerField('prodejní cena zvířete')

    product_amount_sold = models.IntegerField('prodané množství produktu', default=0)
    product_current_price = models.PositiveIntegerField('aktuální cena produktu')


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
    user = models.ForeignKey(User, on_delete=models.RESTRICT, verbose_name='tým')

    slaughtered = models.PositiveIntegerField('prodáno zvířat', default=0)
    stock_size = models.PositiveIntegerField('velikost zásob', default=0)
    money = models.PositiveIntegerField('peníze')

# TODO: check (this function does not even work)
    # def get_ls_sold_total(self) -> int:
    #     ls_actions = TeamLivestockActionHistory.objects.filter(tick=tick, user=user).all()
    #     sold = 0
    #     for ls_action in ls_actions:
    #         sold += ls_action.sold
    #     return sold


class TeamCropActionHistory(models.Model):
    class Meta:
        verbose_name = 'plodiny - historie akcí týmu'
        verbose_name_plural = 'plodiny - historie akcí týmů'
        unique_together = (('tick', 'user', 'crop'),)

    id = models.AutoField(primary_key=True)
    tick = models.ForeignKey(Tick, on_delete=models.CASCADE, verbose_name='minikolo')
    user = models.ForeignKey(User, on_delete=models.RESTRICT, verbose_name='tým')
    crop = models.ForeignKey(Crop, on_delete=models.RESTRICT, verbose_name='plodina')

    bought = models.PositiveIntegerField('koupeno', default=0)
    sold = models.PositiveIntegerField('množství', default=0)


class TeamLivestockActionHistory(models.Model):
    class Meta:
        verbose_name = 'dobytek - historie akcí týmu'
        verbose_name_plural = 'dobytek - historie akcí týmů'
        unique_together = (('tick', 'user', 'livestock'),)

    id = models.AutoField(primary_key=True)
    tick = models.ForeignKey(Tick, on_delete=models.CASCADE, verbose_name='minikolo')
    user = models.ForeignKey(User, on_delete=models.RESTRICT, verbose_name='tým')
    livestock = models.ForeignKey(Livestock, on_delete=models.RESTRICT, verbose_name='dobytek')

    bought = models.PositiveIntegerField('koupeno', default=0)
    sold = models.PositiveIntegerField('prodáno', default=0)
    killed = models.PositiveIntegerField('zabito', default=0)


class TeamCropHistory(models.Model):
    class Meta:
        verbose_name = 'plodiny - historie množství týmu podle stáří'
        verbose_name_plural = 'plodiny - historie množství týmů podle stáří'
        unique_together = (('tick', 'user', 'crop', 'age'),)

    id = models.AutoField(primary_key=True)
    tick = models.ForeignKey(Tick, on_delete=models.CASCADE, verbose_name='minikolo')
    user = models.ForeignKey(User, on_delete=models.RESTRICT, verbose_name='tým')
    crop = models.ForeignKey(Crop, on_delete=models.RESTRICT, verbose_name='plodina')
    age = models.PositiveIntegerField('čas do zkažení produktu')

    amount = models.PositiveIntegerField('množství', default=0)


class TeamLivestockHistory(models.Model):
    class Meta:
        verbose_name = 'dobytek - historie množství týmu podle stáří'
        verbose_name_plural = 'dobytek - historie množství týmů podle stáří'
        unique_together = (('tick', 'user', 'livestock', 'age'),)

    id = models.AutoField(primary_key=True)
    tick = models.ForeignKey(Tick, on_delete=models.CASCADE, verbose_name='minikolo')
    user = models.ForeignKey(User, on_delete=models.RESTRICT, verbose_name='tým')
    livestock = models.ForeignKey(Livestock, on_delete=models.RESTRICT, verbose_name='dobytek')
    age = models.PositiveIntegerField('čas do smrti dobytka')

    amount = models.PositiveIntegerField('množství', default=0)
