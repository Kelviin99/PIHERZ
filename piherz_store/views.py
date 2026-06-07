from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Producto
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .carrito import Carrito

from django.db.models import Q

def index(request):
    q = request.GET.get('q', '').strip()
    if q:
        productos = Producto.objects.filter(
            Q(nombre__icontains=q) |
            Q(descripcion__icontains=q) |
            Q(categoria__nombre__icontains=q)
        )
    else:
        productos = Producto.objects.all()
    return render(request, 'piherz_store/index.html', {'productos': productos, 'q': q})

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, 'piherz_store/detalle.html', {'producto': producto})

def ver_carrito(request):
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

def agregar_al_carrito(request, producto_id):
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id)
        carrito_obj = Carrito(request)
        cantidad = int(request.POST.get('cantidad', 1)) if request.POST.get('cantidad') else 1
        
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

def registro_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden')
            return render(request, 'piherz_store/registro.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El usuario ya existe')
            return render(request, 'piherz_store/registro.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'El email ya está registrado')
            return render(request, 'piherz_store/registro.html')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('index')
    
    return render(request, 'piherz_store/registro.html')

def logout_view(request):
    logout(request)
    return redirect('index')

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