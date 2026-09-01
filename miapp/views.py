from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.models import User

# Importamos tus modelos y formularios
from .models import Producto, Categoria, Carrito, Favorito
from .forms import ProductoForm, RegistroForm

def es_admin(user):
    return user.is_authenticated and user.is_staff

# 🏠 HOME
@login_required
def home(request):
    query = request.GET.get('q')
    categoria = request.GET.get('cat')

    productos_list = Producto.objects.select_related('categoria', 'usuario').all().order_by('-id')

    if categoria:
        productos_list = productos_list.filter(categoria_id=categoria)

    if query:
        productos_list = productos_list.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query)
        )

    # PAGINACIÓN: Muestra 6 productos por página
    paginator = Paginator(productos_list, 6) 
    page_number = request.GET.get('page')
    productos = paginator.get_page(page_number) 

    destacados = Producto.objects.filter(destacado=True)[:3]
    categorias = Categoria.objects.all()

    return render(request, 'home.html', {
        'productos': productos,
        'destacados': destacados,
        'categorias': categorias
    })


# ➕ CREAR
@user_passes_test(es_admin)
def crear(request):
    form = ProductoForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        producto = form.save(commit=False)
        producto.usuario = request.user
        producto.save()
        messages.success(request, '¡Producto creado con éxito!')
        return redirect('home')

    return render(request, 'formulario.html', {'form': form})


# ✏️ EDITAR
@user_passes_test(es_admin)
def editar(request, id):
    producto = get_object_or_404(Producto, id=id)
    form = ProductoForm(request.POST or None, request.FILES or None, instance=producto)

    if form.is_valid():
        form.save()
        messages.success(request, 'Producto actualizado con éxito.')
        return redirect('home')

    return render(request, 'formulario.html', {'form': form})


# 🗑️ ELIMINAR
@user_passes_test(es_admin)
def eliminar(request, id):
    producto = get_object_or_404(Producto, id=id)

    if request.method == "POST":
        producto.delete()
        messages.warning(request, 'Producto eliminado.')
        return redirect('home')

    return render(request, 'confirmar_eliminar.html', {'producto': producto})


# 🔐 REGISTRO
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"¡Bienvenido {user.username}! Tu cuenta ha sido creada.")
            return redirect('home')
    else:
        form = RegistroForm()
    
    return render(request, 'registro.html', {'form': form})


# 🔵 LOGIN
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"¡Qué bueno verte de nuevo, {user.username}! 👋")
            return redirect('home')
        else:
            messages.error(request, "Usuario o contraseña incorrectos. Intentá de nuevo.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


# 🔴 LOGOUT 
def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente. ¡Vuelve pronto!")
    return redirect('home')


# 📄 DETALLE
def detalle(request, id):
    producto = get_object_or_404(Producto, id=id)
    return render(request, 'detalle.html', {'producto': producto})


# 👤 PERFIL
@login_required
def perfil(request):
    productos = Producto.objects.filter(usuario=request.user)
    total = productos.count()

    return render(request, 'perfil.html', {
        'productos': productos,
        'total': total
    })


# 🔎 API BUSCADOR
def buscar_productos(request):
    query = request.GET.get('q', '')

    productos = Producto.objects.filter(
        Q(nombre__icontains=query) |
        Q(descripcion__icontains=query)
    )

    data = []

    for p in productos:
        data.append({
            'id': p.id,
            'nombre': p.nombre,
            'descripcion': p.descripcion,
            'precio': float(p.precio),
            'imagen': p.imagen.url if p.imagen else '',
        })

    return JsonResponse({'productos': data})


# 🛒 CARRITO Y FAVORITOS
@login_required
def agregar_al_carrito(request, id):
    producto = get_object_or_404(Producto, id=id)
    carrito_item, created = Carrito.objects.get_or_create(usuario=request.user, producto=producto)
    
    if not created:
        carrito_item.cantidad += 1
        carrito_item.save()
        
    messages.success(request, f"✨ ¡'{producto.nombre}' agregado a tu carrito!")
    return redirect('ver_carrito') 

@login_required
def ver_carrito(request):
    items = Carrito.objects.filter(usuario=request.user)
    total = sum(item.producto.precio * item.cantidad for item in items)
    
    return render(request, 'carrito.html', {'items': items, 'total': total})

@login_required
def eliminar_del_carrito(request, id):
    item = get_object_or_404(Carrito, id=id, usuario=request.user)
    item.delete()
    messages.warning(request, 'Producto eliminado del carrito.')
    return redirect('ver_carrito')

@login_required
def toggle_favorito(request, id):
    producto = get_object_or_404(Producto, id=id)
    favorito = Favorito.objects.filter(usuario=request.user, producto=producto).first()
    
    if favorito:
        favorito.delete()
        messages.info(request, f'"{producto.nombre}" eliminado de favoritos.')
    else:
        Favorito.objects.create(usuario=request.user, producto=producto)
        messages.success(request, f'"{producto.nombre}" agregado a favoritos. ❤️')
        
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@user_passes_test(es_admin)
def dashboard(request):
    total_productos = Producto.objects.count()
    total_usuarios = User.objects.count()
    total_favoritos = Favorito.objects.count()
    productos = Producto.objects.all().order_by('-id')
    
    return render(request, 'dashboard.html', {
        'total_productos': total_productos,
        'total_usuarios': total_usuarios,
        'total_favoritos': total_favoritos,
        'productos': productos
    })

@login_required
def sumar_cantidad(request, id):
    item = get_object_or_404(Carrito, id=id, usuario=request.user)
    item.cantidad += 1
    item.save()
    messages.success(request, f"Se actualizó la cantidad de '{item.producto.nombre}'.")
    return redirect('ver_carrito')

@login_required
def restar_cantidad(request, id):
    item = get_object_or_404(Carrito, id=id, usuario=request.user)
    if item.cantidad > 1:
        item.cantidad -= 1
        item.save()
        messages.success(request, f"Se actualizó la cantidad de '{item.producto.nombre}'.")
    else:
        item.delete()
        messages.warning(request, f"'{item.producto.nombre}' fue eliminado del carrito.")
    return redirect('ver_carrito')