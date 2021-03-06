from django.db import models

from . import widgets
from .models import *
from django.contrib import admin


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ['name', 'published', 'author', 'tag_list_str']

    formfield_overrides = {
        models.TextField: {'widget': widgets.MarkdownTextField}
    }


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ['name', 'created', 'owner']


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'base_price_buy', 'base_price_sell', 'growth_time', 'rotting_time', 'color']


@admin.register(Livestock)
class CropAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'base_price_buy', 'base_price_sell', 'growth_time', 'color']


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ['id', 'start', 'ticks', 'period', 'crop_storage_size', 'livestock_slaughter_limit', 'start_money']


@admin.register(TeamCropHistory)
class CromHistoryAdmin(admin.ModelAdmin):
    list_display = ['round', 'user', 'tick', 'crop', 'age', 'amount']


@admin.register(TeamLivestockHistory)
class TeamLivestockHistoryAdmin(admin.ModelAdmin):
    list_display = ['round', 'user', 'tick', 'livestock', 'age', 'amount']


@admin.register(TeamHistory)
class TeamHistoryAdmin(admin.ModelAdmin):
    list_display = ['round', 'user', 'tick', 'money']


@admin.register(CropMarketHistory)
class CropMarketHistoryAdmin(admin.ModelAdmin):
    list_display = ['round', 'tick', 'crop', 'amount_sold', 'current_price_buy', 'current_price_sell']


@admin.register(LivestockMarketHistory)
class LivestockMarketHistoryADmin(admin.ModelAdmin):
    list_display = ['round', 'tick', 'livestock', 'amount_sold', 'current_price_buy',
                    'current_price_sell', 'product_amount_sold', 'product_current_price']
