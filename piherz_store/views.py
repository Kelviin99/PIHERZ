from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Producto
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .carrito import Carrito
from .forms import RegistroForm
from django.core.paginator import Paginator

from django.db.models import Q

def index(request):
    try:
        q = request.GET.get('q', '').strip()
        if q:
            productos = Producto.objects.filter(
                Q(nombre__icontains=q) |
                Q(descripcion__icontains=q) |
                Q(categoria__nombre__icontains=q)
            )
        else:
            productos = Producto.objects.all()

        # Paginación: 12 productos por página
        paginator = Paginator(productos, 12)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        return render(request, 'piherz_store/index.html', {
            'productos': page_obj,
            'q': q,
            'page_obj': page_obj
        })
    except Exception as e:
        messages.error(request, 'Error al cargar los productos')
        return render(request, 'piherz_store/index.html', {'productos': [], 'q': ''})

def detalle_producto(request, producto_id):
    try:
        producto = get_object_or_404(Producto, id=producto_id)
        return render(request, 'piherz_store/detalle.html', {'producto': producto})
    except Exception as e:
        messages.error(request, 'Error al cargar el producto')
        return redirect('index')

def ver_carrito(request):
    try:
        carrito_obj = Carrito(request)
        carrito = carrito_obj.carrito
        total = 0
        total_items = 0
        for key, item in carrito.items():
            # Obtener información del producto si no está en el carrito
            if 'nombre' not in item or 'imagen' not in item:
                producto = get_object_or_404(Producto, id=key)
                item['nombre'] = producto.nombre
                item['imagen'] = producto.imagen.url if producto.imagen else ''
            item['subtotal'] = float(item['precio']) * item['cantidad']
            total += item['subtotal']
            total_items += item['cantidad']
        return render(request, 'piherz_store/carrito.html', {'carrito': carrito, 'total': total, 'total_items': total_items})
    except Exception as e:
        messages.error(request, 'Error al cargar el carrito')
        return render(request, 'piherz_store/carrito.html', {'carrito': {}, 'total': 0, 'total_items': 0})

def agregar_al_carrito(request, producto_id):
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id)
        carrito_obj = Carrito(request)
        cantidad = int(request.POST.get('cantidad', 1)) if request.POST.get('cantidad') else 1

        # Validar stock
        if producto.stock < cantidad:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': f'Solo hay {producto.stock} unidades disponibles'
                }, status=400)
            messages.error(request, f'Solo hay {producto.stock} unidades disponibles')
            return redirect('detalle_producto', producto_id=producto_id)

        carrito_obj.agregar(producto, cantidad)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            carrito_cantidad = sum(item['cantidad'] for item in carrito_obj.carrito.values())
            precio_formateado = format(int(producto.precio), ',').replace(',', '.')
            return JsonResponse({
                'status': 'success',
                'producto': producto.nombre,
                'precio': float(producto.precio),
                'precio_formateado': precio_formateado,
                'cantidad': cantidad,
                'carrito_cantidad': carrito_cantidad,
                'message': '¡Listo, recibido!'
            })

        return redirect('ver_carrito')

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

def remover_del_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito_obj = Carrito(request)
    carrito_obj.quitar(producto)
    return redirect('ver_carrito')

def actualizar_carrito(request, producto_id):
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        producto = get_object_or_404(Producto, id=producto_id)
        carrito_obj = Carrito(request)
        
        # Primero quitamos el producto
        carrito_obj.quitar(producto)
        # Luego lo agregamos con la nueva cantidad
        carrito_obj.agregar(producto, cantidad)
        
    return redirect('ver_carrito')

def login_view(request):
    try:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos')
        return render(request, 'piherz_store/login.html')
    except Exception as e:
        messages.error(request, 'Error al iniciar sesión')
        return render(request, 'piherz_store/login.html')

def registro_view(request):
    try:
        if request.method == 'POST':
            form = RegistroForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']

                user = User.objects.create_user(username=username, email=email, password=password)
                login(request, user)
                return redirect('index')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, error)
                return render(request, 'piherz_store/registro.html', {'form': form})

        form = RegistroForm()
        return render(request, 'piherz_store/registro.html', {'form': form})
    except Exception as e:
        messages.error(request, 'Error al registrar usuario')
        form = RegistroForm()
        return render(request, 'piherz_store/registro.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')

def mis_compras(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # Obtener items del carrito del usuario
    from .models import CarritoItem
    carrito_items = CarritoItem.objects.filter(usuario=request.user).order_by('-creado')

    # Calcular total
    total = 0
    for item in carrito_items:
        total += item.subtotal()

    return render(request, 'piherz_store/mis_compras.html', {
        'carrito_items': carrito_items,
        'total': total
    })

def obtener_carrito_cantidad(request):
    """Vista para obtener la cantidad actual del carrito via AJAX"""
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        carrito_obj = Carrito(request)
        carrito_cantidad = sum(item['cantidad'] for item in carrito_obj.carrito.values())
        
        # Si estamos en la página del carrito, devolver información completa
        es_pagina_carrito = request.GET.get('pagina_carrito', 'false') == 'true'
        
        if es_pagina_carrito:
            # Devolver información completa del carrito
            carrito_completo = []
            total = 0
            for key, item in carrito_obj.carrito.items():
                # Obtener información del producto si no está en el carrito
                if 'nombre' not in item or 'imagen' not in item:
                    producto = get_object_or_404(Producto, id=key)
                    item['nombre'] = producto.nombre
                    item['imagen'] = producto.imagen.url if producto.imagen else ''
                item['subtotal'] = float(item['precio']) * item['cantidad']
                total += item['subtotal']
                carrito_completo.append({
                    'key': key,
                    'nombre': item['nombre'],
                    'imagen': item['imagen'],
                    'precio': item['precio'],
                    'cantidad': item['cantidad'],
                    'subtotal': item['subtotal']
                })
            
            return JsonResponse({
                'status': 'success',
                'carrito_cantidad': carrito_cantidad,
                'carrito_completo': carrito_completo,
                'total': total
            })
        else:
            # Solo devolver la cantidad
            return JsonResponse({
                'status': 'success',
                'carrito_cantidad': carrito_cantidad
            })
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)