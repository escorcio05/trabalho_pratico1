from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Rotas dos Filmes
    path('', views.lista_filmes, name='lista_filmes'),
    path('filme/<int:filme_id>/', views.detalhe_filme, name='detalhe_filme'),

    path('filme/adicionar/', views.adicionar_filme, name='adicionar_filme'),
    path('editar-filme/<int:id>/', views.editar_filme, name='editar_filme'),

    # Rota de Registo (a que criámos na views.py)
    # Correto: apenas o nome da função, sem parênteses e sem template_name aqui
    path('registo/', views.registo, name='registo'),
    # Rotas de Login/Logout (usando as views prontas do Django)
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # ... os teus outros urls ...
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),

    path('favoritos/', views.meus_favoritos, name='meus_favoritos'),
    path('guardados/', views.meus_guardados, name='meus_guardados'),
    path('favorito/toggle/<int:filme_id>/', views.toggle_favorito, name='toggle_favorito'),
    path('guardado/toggle/<int:filme_id>/', views.toggle_guardado, name='toggle_guardado'),


    ]
