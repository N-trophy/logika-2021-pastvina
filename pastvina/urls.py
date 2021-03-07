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

    path('api/md_to_html', views.handler_markdown_to_html, name='md_to_html'),
    path('favicon.ico', RedirectView.as_view(url='/static/pastvina/img/logo.png')),

    path('rules/', views.page_rules, name='rules'),

    path('game/', views.page_game_overview, name='game_overview'),
    path('game/<int:round_id>/', views.page_game, name='game'),
    path('game/<int:round_id>/update', views.game_update, name='game_update'),
    path('game/<int:round_id>/trade', views.game_trade, name='game_trade'),

    path('', views.page_index, name='index'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
