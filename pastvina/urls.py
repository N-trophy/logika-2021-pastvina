from django.contrib import admin
from django.urls import path
from pastvina import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.page_login, name='login'),
    path('logout/', views.handler_logout, name='logout'),

    path('%s<path:path>' % settings.PRIVATE_URL, views.protected_serve, {'document_root': settings.PRIVATE_ROOT}),
    path('api/md_to_html', views.handler_markdown_to_html, name='md_to_html'),

    path('game/', views.page_game, name='game'),
    path('game/update', views.game_update, name='game_update'),
    path('', views.page_index, name='index'),
    path('<path:path>', views.page_static, name='static_page'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
