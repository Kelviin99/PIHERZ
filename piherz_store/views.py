from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Producto

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
    carrito = request.session.get('carrito', {})
    total = 0
    total_items = 0
    for item in carrito.values():
        item['subtotal'] = float(item['precio']) * item['cantidad']
        total += item['subtotal']
        total_items += item['cantidad']
    return render(request, 'piherz_store/carrito.html', {'carrito': carrito, 'total': total, 'total_items': total_items})

def agregar_al_carrito(request, producto_id):
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id)
        carrito = request.session.get('carrito', {})
        p_id = str(producto_id)
        cantidad = int(request.POST.get('cantidad', 1)) if request.POST.get('cantidad') else 1

        if p_id in carrito:
            carrito[p_id]['cantidad'] += cantidad
        else:
            carrito[p_id] = {
                'nombre': producto.nombre,
                'precio': float(producto.precio),
                'cantidad': cantidad,
                'imagen': producto.imagen.url if producto.imagen else ''
            }

        request.session['carrito'] = carrito
        request.session.modified = True

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            carrito_cantidad = sum(item['cantidad'] for item in carrito.values())
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
    carrito = request.session.get('carrito', {})
    p_id = str(producto_id)
    if p_id in carrito:
        del carrito[p_id]
        request.session['carrito'] = carrito
        request.session.modified = True
    return redirect('ver_carrito')

def actualizar_carrito(request, producto_id):
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        carrito = request.session.get('carrito', {})
        p_id = str(producto_id)
        if p_id in carrito:
            carrito[p_id]['cantidad'] = cantidad
            request.session['carrito'] = carrito
            request.session.modified = True
    return redirect('ver_carrito')