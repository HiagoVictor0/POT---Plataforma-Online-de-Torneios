from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('painel/', views.painel_view, name='painel'),
    path('logout/', views.logout_view, name='logout'),
    path('criar_torneio/', views.criar_torneio_view, name='criar_torneio'),
    path('inscricoes/', views.inscricoes_view, name='inscricoes'),
    path('resultados/', views.resultados_view, name='resultados')
]
