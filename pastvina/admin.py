from django.db import models

from . import widgets
from .models import User, Contribution, StaticPage, MediaFile, Menu
from django.contrib import admin


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'is_superuser', 'is_staff']


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ['name', 'published', 'author', 'tag_list_str']

    formfield_overrides = {
        models.TextField: {'widget': widgets.MarkdownTextField}
    }


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ['name']
    formfield_overrides = {
        models.TextField: {'widget': widgets.MarkdownTextField}
    }


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ['name', 'created', 'owner']
