from django.urls import path
from django.contrib import messages
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
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/eliminar/<int:id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('favoritos/toggle/<int:id>/', views.toggle_favorito, name='toggle_favorito'),
]