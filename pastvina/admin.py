from django.db import models

from . import widgets
from .models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.timezone import localtime


UserAdmin.list_display = (
    'username', 'email', 'first_name', 'last_name', 'is_active', 'is_superuser'
)


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
        'index',
        'name',
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
        '_start',
        ]

    def _start(self, obj):
        return localtime(obj.start).strftime('%H:%M:%S.%f')


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
        'base_price_buy',
        'base_price_sell',
        'growth_time',
        'life_time',
        'color',
        'product_name',
        'product_price',
        'consumption_type',
        'consumption',
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

    list_filter = [
        'tick__round',
        'crop',
        'tick__index',
        ]


@admin.register(LivestockMarketHistory)
class LivestockMarketHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'tick',
        'livestock',
        'current_price_buy',
        'current_price_sell',
        'amount_sold',
        'product_current_price',
        'product_amount_sold',
        ]

    list_filter = [
        'tick__round',
        'livestock',
        'tick__index',
        ]


@admin.register(TeamHistory)
class TeamHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'tick',
        'user',
        'money',
        'slaughtered',
        ]

    list_filter = [
        'tick__round',
        'user'
    ]


@admin.register(TeamCropActionHistory)
class TeamCropActionHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'tick',
        'user',
        'crop',
        'bought',
        'sold',
        ]


@admin.register(TeamLivestockActionHistory)
class TeamLivestockActionHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'tick',
        'user',
        'livestock',
        'bought',
        'sold',
        'killed',
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

    list_filter = [
        'tick__round',
        'user',
        'crop',
        'tick__index',
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

    list_filter = [
        'tick__round',
        'user',
        'livestock',
        'tick__index',
        ]
