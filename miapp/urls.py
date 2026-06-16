from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('crear/', views.crear, name='crear'),
    path('editar/<int:id>/', views.editar, name='editar'),
    path('eliminar/<int:id>/', views.eliminar, name='eliminar'),

    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('producto/<int:id>/', views.detalle, name='detalle'),
    path('perfil/', views.perfil, name='perfil'),
    path('api/buscar/', views.buscar_productos, name='buscar_productos'),
]