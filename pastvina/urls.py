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

    path('rules/', views.page_rules, name='rules'),

    path('game/', views.page_game_overview, name='game_overview'),

    # Chceme samostatnou stránku, kde budou vypsané všechny statistiky?
    path('game/stats', views.page_team_game_stats, name='team_game_stats'), 

    path('game/<int:round_id>/', views.page_game, name='game'),
    path('game/<int:round_id>/update', views.game_update, name='game_update'),
    path('game/<int:round_id>/trade', views.game_trade, name='game_trade'),
    path('game/<int:round_id>/statistics', views.statistics, name='statistics'),

    # TODO: remove
    path('game/test_s', views.test_s, name='test_s'),

    path('', views.page_index, name='index'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
