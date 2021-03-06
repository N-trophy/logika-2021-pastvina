from django.db import models

from . import widgets
from .models import Contribution, MediaFile, Crop, Livestock
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
