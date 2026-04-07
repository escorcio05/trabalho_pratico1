from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Rotas dos Filmes
    path('', views.lista_filmes, name='lista_filmes'),
    path('filme/<int:filme_id>/', views.detalhe_filme, name='detalhe_filme'),

    # Rota de Registo (a que criámos na views.py)
    path('registo/', views.registo, name='registo'),

    # Rotas de Login/Logout (usando as views prontas do Django)
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]