from django.contrib import admin
from django.urls import path
from pastvina import views
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.page_login, name='login'),
    path('logout/', views.handler_logout, name='logout'),

    path('favicon.ico', RedirectView.as_view(url='/static/pastvina/img/logo.png')),

    path('user_activate/', views.user_activate, name='activate'),

    path('time_check/', views.time_check, name='time_check'),
    path('time_check/ping', views.time_check_ping, name='time_check_ping'),

    path('rules/', views.page_rules, name='rules'),

    path('game/', views.page_game_overview, name='game_overview'),

    path('game/<int:round_id>/', views.page_game, name='game'),
    path('game/<int:round_id>/update', views.game_update, name='game_update'),
    path('game/<int:round_id>/trade', views.game_trade, name='game_trade'),
    path('game/<int:round_id>/statistics/', views.statistics, name='round_stats'),
    path('game/<int:round_id>/replay/<int:update_ms>', views.replay, name='round_replay'),

    path('', views.page_index, name='index'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
