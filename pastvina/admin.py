from django.db import models

from . import widgets
from .models import *
from django.contrib import admin


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'published',
        'public_from',
        'author',
        ]


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'start',
        'reload_time',
        'is_test',
        'ticks',
        'period',
        'start_money',
        'crop_storage_size',
        'livestock_slaughter_limit',
        ]


@admin.register(Tick)
class TickAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'index',
        'round',
        'start',
        ]


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'growth_time',
        'rotting_time',
        'base_price_buy',
        'base_price_sell',
        'color',
        ]


@admin.register(Livestock)
class LivestockAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'growth_time',
        'life_time',
        'base_price_buy',
        'base_price_sell',
        'product_name',
        'product_price',
        'consumption_type',
        'consumption',
        'color',
        ]


@admin.register(CropMarketHistory)
class CropMarketHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'tick',
        'crop',
        'current_price_buy',
        'current_price_sell',
        'amount_sold',
        ]


@admin.register(LivestockMarketHistory)
class LivestockMarketHistoryADmin(admin.ModelAdmin):
    list_display = [
        'tick',
        'livestock',
        'current_price_buy',
        'current_price_sell',
        'amount_sold',
        'product_current_price',
        'product_amount_sold',
        ]


@admin.register(TeamHistory)
class TeamHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'tick',
        'user',
        'money',
        'slaughtered',
        ]


@admin.register(TeamCropHistory)
class TeamCropHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'tick',
        'user',
        'crop',
        'age',
        'amount',
        ]


@admin.register(TeamLivestockHistory)
class TeamLivestockHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'tick',
        'user',
        'livestock',
        'age',
        'amount',
        ]
