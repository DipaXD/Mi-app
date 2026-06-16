from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Producto
from .forms import ProductoForm, RegistroForm
from django.db.models import Q
from .models import Producto, Categoria


# 🏠 HOME (con buscador + usuario)
@login_required
def home(request):
    query = request.GET.get('q')
    categoria = request.GET.get('cat')

    productos = Producto.objects.all()

    if categoria:
        productos = productos.filter(categoria_id=categoria)

    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query)
        )

    destacados = Producto.objects.filter(destacado=True)[:3]
    categorias = Categoria.objects.all()

    return render(request, 'home.html', {
        'productos': productos,
        'destacados': destacados,
        'categorias': categorias
    })

# ➕ CREAR PRODUCTO
@login_required
def crear(request):
    form = ProductoForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        producto = form.save(commit=False)
        producto.usuario = request.user
        producto.save()
        return redirect('home')

    return render(request, 'formulario.html', {'form': form})


# ✏️ EDITAR
@login_required
def editar(request, id):
    producto = get_object_or_404(Producto, id=id, usuario=request.user)

    form = ProductoForm(request.POST or None, instance=producto)

    if form.is_valid():
        form.save()
        return redirect('home')

    return render(request, 'formulario.html', {'form': form})


# 🗑️ ELIMINAR
@login_required
def eliminar(request, id):
    producto = get_object_or_404(Producto, id=id, usuario=request.user)

    if request.method == "POST":
        producto.delete()
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
            'precio': p.precio,
            'imagen': p.imagen.url if p.imagen else '',
            'usuario_id': p.usuario.id if p.usuario else None
        })

    return JsonResponse({'productos': data})