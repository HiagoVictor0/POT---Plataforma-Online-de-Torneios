from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('painel/', views.painel_view, name='painel'),
    path('logout/', views.logout_view, name='logout'),
    path('criar_torneio/', views.criar_torneio_view, name='criar_torneio'),
    path('inscricoes/', views.inscricoes_view, name='inscricoes'),
   
    path('criar_equipe/', views.criar_equipe_view, name='criar_equipe'),
    path('dashboard_equipe/', views.dashboard_equipe_view, name='dashboard_equipe'),
    path('dashboard_equipe/<int:equipe_id>/', views.dashboard_equipe_view, name='dashboard_equipe_detail'),
    path('chaveamento/<int:torneio_id>/', views.chaveamento_view, name='chaveamento'),
]
