from django.contrib import admin
from django.urls import path, include
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.lista_filmes, name='lista_filmes'),
    path('filme/<int:filme_id>/', views.detalhe_filme, name='detalhe_filme'),
    path('accounts/', include('django.contrib.auth.urls')),
]