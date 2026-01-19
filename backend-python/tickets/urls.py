from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # auth e registro
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registro/', views.registro, name='registro'),

    # utils de dev
    path('criar-teste/', views.criar_usuario_teste, name='criar_usuario_teste'),

    # perfil
    path('perfil/trocar-senha/', views.perfil_trocar_senha, name='perfil_trocar_senha'),

    # gestao de usuarios (para admin)
    path('gestao/usuarios/', views.gerenciar_usuarios, name='gerenciar_usuarios'),
    path('gestao/usuarios/<int:user_id>/', views.gerenciar_usuarios, name='gerenciar_usuarios'), # carrega usuario na sidebar
    path('gestao/grupos/criar/', views.criar_grupo_sistema, name='criar_grupo_sistema'),
    
    # acoes em massa
    path('gestao/usuarios/massa/', views.acao_em_massa_usuarios, name='acao_em_massa_usuarios'),
    path('gestao/usuarios/exportar/', views.exportar_usuarios, name='exportar_usuarios'),

    # crud de usuarios
    path('gestao/novo-usuario/', views.criar_usuario_sistema, name='criar_usuario_sistema'),
    path('gestao/usuarios/editar/<int:user_id>/', views.editar_usuario_post, name='editar_usuario_post'),
    path('gestao/usuarios/status/<int:pk>/', views.alternar_status_usuario, name='alternar_status_usuario'),
    path('gestao/usuarios/excluir/<int:pk>/', views.excluir_usuario, name='excluir_usuario'),

    # chamados
    path('', views.home, name='home'),
    path('novo/', views.novo_chamado, name='novo_chamado'),
    path('chamado/<int:pk>/', views.editar_chamado, name='editar_chamado'),
    path('chamado/<int:pk>/excluir/', views.excluir_chamado, name='excluir_chamado'),

    # setores
    path('setores/novo/', views.gerenciar_setores, name='gerenciar_setores'),
    path('setores/excluir/<int:pk>/', views.excluir_setor, name='excluir_setor'),
]