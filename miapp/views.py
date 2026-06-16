from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from .models import Carrito
from .models import Favorito
from django.core.paginator import Paginator
from django.contrib import messages

from .models import Producto, Categoria
from .forms import ProductoForm, RegistroForm
from django.contrib.auth.decorators import user_passes_test

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

    # 👈 PAGINACIÓN: Muestra 6 productos por página
    paginator = Paginator(productos_list, 6) 
    page_number = request.GET.get('page')
    productos = paginator.get_page(page_number) # Esto reemplaza tu antigua variable 'productos'

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
    # 👇 Quitamos la restricción de usuario
    producto = get_object_or_404(Producto, id=id)
    form = ProductoForm(request.POST or None, instance=producto)

    if form.is_valid():
        form.save()
        messages.success(request, 'Producto actualizado con éxito.')
        return redirect('home')

    return render(request, 'formulario.html', {'form': form})


# 🗑️ ELIMINAR
@user_passes_test(es_admin)
def eliminar(request, id):
    # 👇 Quitamos la restricción de usuario
    producto = get_object_or_404(Producto, id=id)

    if request.method == "POST":
        producto.delete()
        messages.warning(request, 'Producto eliminado.')
        return redirect('home')

    return render(request, 'confirmar_eliminar.html', {'producto': producto})

# 🔐 REGISTRO
def registro(request):
    form = RegistroForm(request.POST or None)

    if form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()

        login(request, user)
        return redirect('home')

    return render(request, 'registro.html', {'form': form})


# 🔵 LOGIN
def login_view(request):
    form = AuthenticationForm(data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('home')

    return render(request, 'login.html', {'form': form})


# 🔴 LOGOUT
def logout_view(request):
    logout(request)
    return redirect('login')


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


@login_required
def agregar_al_carrito(request, id):
    producto = get_object_or_404(Producto, id=id)
    # Busca si ya está en el carrito, si no, lo crea
    carrito_item, created = Carrito.objects.get_or_create(usuario=request.user, producto=producto)
    
    if not created:
        carrito_item.cantidad += 1
        carrito_item.save()
        
    messages.success(request, f'"{producto.nombre}" agregado al carrito.')
    return redirect('home')

@login_required
def ver_carrito(request):
    items = Carrito.objects.filter(usuario=request.user)
    # Calcula el total iterando los items
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
    # Busca si existe el favorito
    favorito = Favorito.objects.filter(usuario=request.user, producto=producto).first()
    
    if favorito:
        favorito.delete()
        messages.info(request, f'"{producto.nombre}" eliminado de favoritos.')
    else:
        Favorito.objects.create(usuario=request.user, producto=producto)
        messages.success(request, f'"{producto.nombre}" agregado a favoritos. ❤️')
        
    # Redirige a la misma página donde estaba el usuario
    return redirect(request.META.get('HTTP_REFERER', 'home'))