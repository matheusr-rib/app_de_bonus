"""
URL configuration for bonus_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from usuarios.views import LoginCustomView,admin_usuarios_view
from campanhas.views import (
    CampanhaListView,
    CampanhaCreateView,
    CampanhaControleView,
    CampanhaUpdateView,
    CampanhaDeleteView
)
from historico.views import historico_listagem
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('campanhas/', CampanhaListView.as_view(), name='campanha_list'),
    path('nova/', CampanhaCreateView.as_view(), name='campanha_create'),
    path('login/', LoginCustomView.as_view(), name='login'),
    path('gerenciar/', admin_usuarios_view, name='admin_usuarios'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('campanhas/controle/', CampanhaControleView.as_view(), name='campanha_controle'),
    path('campanhas/<int:pk>/editar/', CampanhaUpdateView.as_view(), name='campanha_editar'),
    path('campanhas/<int:pk>/deletar/', CampanhaDeleteView.as_view(), name='campanha_deletar'),
    path('historico/', historico_listagem, name='historico_listagem'),

]