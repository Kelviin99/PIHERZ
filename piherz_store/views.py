from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Producto, Direccion, Pedido, PedidoItem, Reseña, ListaDeseos, Newsletter
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .carrito import Carrito
from .forms import RegistroForm, DireccionForm, CheckoutForm, PerfilForm, ReseñaForm
from django.core.paginator import Paginator
from django.db import transaction
from django.conf import settings
import stripe

from django.db.models import Q

stripe.api_key = settings.STRIPE_SECRET_KEY

def index(request):
    try:
        q = request.GET.get('q', '').strip()
        categoria = request.GET.get('categoria', '')
        precio_min = request.GET.get('precio_min', '')
        precio_max = request.GET.get('precio_max', '')
        stock = request.GET.get('stock', '')
        
        productos = Producto.objects.all()
        
        # Filtro por búsqueda
        if q:
            productos = productos.filter(
                Q(nombre__icontains=q) |
                Q(descripcion__icontains=q) |
                Q(categoria__nombre__icontains=q)
            )
        
        # Filtro por categoría
        if categoria:
            productos = productos.filter(categoria__nombre=categoria)
        
        # Filtro por precio mínimo
        if precio_min:
            productos = productos.filter(precio__gte=precio_min)
        
        # Filtro por precio máximo
        if precio_max:
            productos = productos.filter(precio__lte=precio_max)
        
        # Filtro por stock
        if stock == 'disponible':
            productos = productos.filter(stock__gt=0)
        elif stock == 'agotado':
            productos = productos.filter(stock=0)

        # Obtener categorías para el filtro
        from .models import Categoria
        categorias = Categoria.objects.all()

        # Paginación: 12 productos por página
        paginator = Paginator(productos, 12)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        return render(request, 'piherz_store/index.html', {
            'productos': page_obj,
            'q': q,
            'page_obj': page_obj,
            'categorias': categorias,
            'categoria_seleccionada': categoria,
            'precio_min': precio_min,
            'precio_max': precio_max,
            'stock': stock
        })
    except Exception as e:
        messages.error(request, 'Error al cargar los productos')
        return render(request, 'piherz_store/index.html', {'productos': [], 'q': ''})

def detalle_producto(request, producto_id):
    try:
        producto = get_object_or_404(Producto, id=producto_id)
        
        # Obtener productos relacionados de la misma categoría (excluyendo el producto actual)
        productos_relacionados = Producto.objects.filter(
            categoria=producto.categoria
        ).exclude(id=producto.id)[:4]
        
        # Verificar si el usuario puede agregar reseña
        puede_agregar_resena = False
        if request.user.is_authenticated:
            puede_agregar_resena = not Reseña.objects.filter(
                producto=producto, 
                usuario=request.user
            ).exists()
        
        # Verificar si el producto está en la lista de deseos del usuario
        en_lista_deseos = False
        if request.user.is_authenticated:
            en_lista_deseos = ListaDeseos.objects.filter(
                producto=producto,
                usuario=request.user
            ).exists()
        
        return render(request, 'piherz_store/detalle.html', {
            'producto': producto,
            'productos_relacionados': productos_relacionados,
            'puede_agregar_resena': puede_agregar_resena,
            'en_lista_deseos': en_lista_deseos
        })
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

def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para realizar un pedido')
        return redirect('login')
    
    carrito_obj = Carrito(request)
    carrito = carrito_obj.carrito
    
    if not carrito:
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('ver_carrito')
    
    # Calcular total del carrito
    total = 0
    for key, item in carrito.items():
        producto = get_object_or_404(Producto, id=key)
        item['subtotal'] = float(item['precio']) * item['cantidad']
        total += item['subtotal']
    
    costo_envio = 0  # Puedes cambiar esto según tu lógica de envío
    
    if request.method == 'POST':
        checkout_form = CheckoutForm(request.POST, usuario=request.user)
        direccion_form = DireccionForm(request.POST)
        
        if checkout_form.is_valid():
            direccion = None
            direccion_texto = None
            
            # Determinar qué dirección usar
            if checkout_form.cleaned_data['usar_direccion_nueva']:
                if direccion_form.is_valid():
                    direccion = direccion_form.save(commit=False)
                    direccion.usuario = request.user
                    direccion.save()
                    
                    # Si es predeterminada, quitar predeterminada de otras
                    if direccion.es_predeterminada:
                        Direccion.objects.filter(usuario=request.user).exclude(id=direccion.id).update(es_predeterminada=False)
                else:
                    messages.error(request, 'Por favor completa los datos de la dirección')
                    return render(request, 'piherz_store/checkout.html', {
                        'checkout_form': checkout_form,
                        'direccion_form': direccion_form,
                        'carrito': carrito,
                        'total': total,
                        'costo_envio': costo_envio,
                        'total_final': total + costo_envio
                    })
            else:
                direccion_texto = checkout_form.cleaned_data['direccion_existente']
                if direccion_texto:
                    # Crear dirección temporal basada en el texto
                    direccion = Direccion.objects.create(
                        usuario=request.user,
                        direccion=direccion_texto,
                        nombre=request.user.first_name or 'Usuario',
                        apellido=request.user.last_name or '',
                        ciudad='Ciudad',
                        departamento='Departamento',
                        codigo_postal='000000',
                        telefono='0000000000',
                        es_predeterminada=False
                    )
            
            if not direccion:
                messages.error(request, 'Debes escribir o crear una dirección de envío')
                return render(request, 'piherz_store/checkout.html', {
                    'checkout_form': checkout_form,
                    'direccion_form': direccion_form,
                    'carrito': carrito,
                    'total': total,
                    'costo_envio': costo_envio,
                    'total_final': total + costo_envio
                })
            
            metodo_pago = checkout_form.cleaned_data['metodo_pago']
            
            # Si es pago con Stripe, crear sesión de pago
            if metodo_pago == 'stripe':
                try:
                    # Crear sesión de pago con Stripe
                    session = stripe.checkout.Session.create(
                        payment_method_types=['card'],
                        line_items=[{
                            'price_data': {
                                'currency': 'cop',
                                'product_data': {
                                    'name': f'Pedido #{request.user.username}',
                                },
                                'unit_amount': int((total + costo_envio) * 100),  # Stripe usa centavos
                            },
                            'quantity': 1,
                        }],
                        mode='payment',
                        success_url=request.build_absolute_uri(f'/pedido-exito/?pedido_id={{CHECKOUT_SESSION_ID}}'),
                        cancel_url=request.build_absolute_uri('/checkout/'),
                        metadata={
                            'usuario_id': str(request.user.id),
                            'direccion_id': str(direccion.id),
                            'subtotal': str(total),
                            'costo_envio': str(costo_envio),
                            'total': str(total + costo_envio),
                            'notas': checkout_form.cleaned_data['notas'] or '',
                        }
                    )
                    
                    # Guardar información temporal del carrito en sesión para procesar después del pago
                    request.session['checkout_data'] = {
                        'direccion_id': direccion.id,
                        'subtotal': str(total),
                        'costo_envio': str(costo_envio),
                        'total': str(total + costo_envio),
                        'notas': checkout_form.cleaned_data['notas'] or '',
                        'stripe_session_id': session.id,
                    }
                    
                    return redirect(session.url, code=303)
                    
                except Exception as e:
                    messages.error(request, f'Error al procesar el pago: {str(e)}')
                    return render(request, 'piherz_store/checkout.html', {
                        'checkout_form': checkout_form,
                        'direccion_form': direccion_form,
                        'carrito': carrito,
                        'total': total,
                        'costo_envio': costo_envio,
                        'total_final': total + costo_envio
                    })
            
            # Si es contra entrega, crear el pedido directamente
            else:
                # Crear el pedido
                with transaction.atomic():
                    pedido = Pedido.objects.create(
                        usuario=request.user,
                        direccion=direccion,
                        estado='pendiente',
                        subtotal=total,
                        costo_envio=costo_envio,
                        total=total + costo_envio,
                        notas=checkout_form.cleaned_data['notas']
                    )
                    
                    # Crear items del pedido
                    for key, item in carrito.items():
                        producto = get_object_or_404(Producto, id=key)
                        PedidoItem.objects.create(
                            pedido=pedido,
                            producto=producto,
                            nombre_producto=producto.nombre,
                            precio_unitario=item['precio'],
                            cantidad=item['cantidad']
                        )
                    
                    # Limpiar el carrito
                    carrito_obj.limpiar()
                
                messages.success(request, f'¡Pedido #{pedido.numero_pedido} creado exitosamente!')
                return redirect('detalle_pedido', pedido_id=pedido.id)
    else:
        checkout_form = CheckoutForm(usuario=request.user)
        direccion_form = DireccionForm()
    
    return render(request, 'piherz_store/checkout.html', {
        'checkout_form': checkout_form,
        'direccion_form': direccion_form,
        'carrito': carrito,
        'total': total,
        'costo_envio': costo_envio,
        'total_final': total + costo_envio,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    })

def historial_pedidos(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-creado')
    
    return render(request, 'piherz_store/historial_pedidos.html', {'pedidos': pedidos})

def detalle_pedido(request, pedido_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    
    return render(request, 'piherz_store/detalle_pedido.html', {'pedido': pedido})

def pedido_exito(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    session_id = request.GET.get('pedido_id')
    
    if not session_id:
        messages.error(request, 'No se pudo procesar el pago')
        return redirect('checkout')
    
    try:
        # Verificar la sesión de pago con Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == 'paid':
            # Obtener datos de la sesión
            checkout_data = request.session.get('checkout_data')
            
            if checkout_data and checkout_data.get('stripe_session_id') == session_id:
                direccion = get_object_or_404(Direccion, id=checkout_data['direccion_id'])
                
                # Crear el pedido
                with transaction.atomic():
                    pedido = Pedido.objects.create(
                        usuario=request.user,
                        direccion=direccion,
                        estado='procesando',  # Pagado, así que pasa a procesando
                        subtotal=checkout_data['subtotal'],
                        costo_envio=checkout_data['costo_envio'],
                        total=checkout_data['total'],
                        notas=checkout_data['notas']
                    )
                    
                    # Crear items del pedido desde el carrito
                    carrito_obj = Carrito(request)
                    carrito = carrito_obj.carrito
                    
                    for key, item in carrito.items():
                        producto = get_object_or_404(Producto, id=key)
                        PedidoItem.objects.create(
                            pedido=pedido,
                            producto=producto,
                            nombre_producto=producto.nombre,
                            precio_unitario=item['precio'],
                            cantidad=item['cantidad']
                        )
                    
                    # Limpiar el carrito y la sesión temporal
                    carrito_obj.limpiar()
                    del request.session['checkout_data']
                
                messages.success(request, f'¡Pago exitoso! Pedido #{pedido.numero_pedido} creado.')
                return redirect('detalle_pedido', pedido_id=pedido.id)
            else:
                messages.error(request, 'Error al procesar el pedido. Por favor intenta nuevamente.')
                return redirect('checkout')
        else:
            messages.error(request, 'El pago no fue completado')
            return redirect('checkout')
            
    except Exception as e:
        messages.error(request, f'Error al procesar el pago: {str(e)}')
        return redirect('checkout')

def perfil_usuario(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado exitosamente')
            return redirect('perfil_usuario')
    else:
        form = PerfilForm(instance=request.user)
    
    direcciones = Direccion.objects.filter(usuario=request.user)
    
    return render(request, 'piherz_store/perfil_usuario.html', {
        'form': form,
        'direcciones': direcciones
    })

def agregar_direccion(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        direccion = Direccion(
            usuario=request.user,
            nombre=request.POST.get('nombre'),
            apellido=request.POST.get('apellido'),
            direccion=request.POST.get('direccion'),
            ciudad=request.POST.get('ciudad'),
            departamento=request.POST.get('departamento'),
            codigo_postal=request.POST.get('codigo_postal'),
            telefono=request.POST.get('telefono'),
            es_predeterminada=request.POST.get('es_predeterminada') == 'on'
        )
        direccion.save()
        
        # Si es predeterminada, quitar predeterminada de otras
        if direccion.es_predeterminada:
            Direccion.objects.filter(usuario=request.user).exclude(id=direccion.id).update(es_predeterminada=False)
        
        messages.success(request, 'Dirección agregada exitosamente')
        return redirect('perfil_usuario')
    
    return redirect('perfil_usuario')

def cambiar_contrasena(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        contrasena_actual = request.POST.get('contrasena_actual')
        nueva_contrasena = request.POST.get('nueva_contrasena')
        confirmar_contrasena = request.POST.get('confirmar_contrasena')
        
        if not request.user.check_password(contrasena_actual):
            messages.error(request, 'La contraseña actual es incorrecta')
            return render(request, 'piherz_store/cambiar_contrasena.html')
        
        if nueva_contrasena != confirmar_contrasena:
            messages.error(request, 'Las contraseñas nuevas no coinciden')
            return render(request, 'piherz_store/cambiar_contrasena.html')
        
        if len(nueva_contrasena) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres')
            return render(request, 'piherz_store/cambiar_contrasena.html')
        
        request.user.set_password(nueva_contrasena)
        request.user.save()
        
        messages.success(request, 'Contraseña cambiada exitosamente. Por favor inicia sesión nuevamente.')
        return redirect('login')
    
    return render(request, 'piherz_store/cambiar_contrasena.html')

def agregar_resena(request, producto_id):
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para dejar una reseña')
        return redirect('login')
    
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Verificar si el usuario ya tiene una reseña para este producto
    if Reseña.objects.filter(producto=producto, usuario=request.user).exists():
        messages.warning(request, 'Ya has dejado una reseña para este producto')
        return redirect('detalle_producto', producto_id=producto_id)
    
    if request.method == 'POST':
        form = ReseñaForm(request.POST)
        if form.is_valid():
            reseña = form.save(commit=False)
            reseña.producto = producto
            reseña.usuario = request.user
            reseña.save()
            messages.success(request, '¡Reseña agregada exitosamente!')
            return redirect('detalle_producto', producto_id=producto_id)
    else:
        form = ReseñaForm()
    
    return render(request, 'piherz_store/agregar_resena.html', {
        'form': form,
        'producto': producto
    })

def lista_deseos(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    lista_deseos = ListaDeseos.objects.filter(usuario=request.user).select_related('producto')
    
    return render(request, 'piherz_store/lista_deseos.html', {
        'lista_deseos': lista_deseos
    })

def agregar_a_lista_deseos(request, producto_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Verificar si ya está en la lista de deseos
    if ListaDeseos.objects.filter(usuario=request.user, producto=producto).exists():
        messages.info(request, 'Este producto ya está en tu lista de deseos')
    else:
        ListaDeseos.objects.create(usuario=request.user, producto=producto)
        messages.success(request, 'Producto agregado a tu lista de deseos')
    
    return redirect('detalle_producto', producto_id=producto_id)

def quitar_de_lista_deseos(request, producto_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    producto = get_object_or_404(Producto, id=producto_id)
    
    try:
        item = ListaDeseos.objects.get(usuario=request.user, producto=producto)
        item.delete()
        messages.success(request, 'Producto eliminado de tu lista de deseos')
    except ListaDeseos.DoesNotExist:
        messages.warning(request, 'Este producto no está en tu lista de deseos')
    
    return redirect('lista_deseos')

def contacto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        asunto = request.POST.get('asunto')
        mensaje = request.POST.get('mensaje')
        
        if nombre and email and asunto and mensaje:
            # Aquí puedes agregar lógica para enviar el email
            # Por ahora, solo mostramos un mensaje de éxito
            messages.success(request, '¡Mensaje enviado exitosamente! Nos pondremos en contacto contigo pronto.')
            return redirect('contacto')
        else:
            messages.error(request, 'Por favor completa todos los campos')
    
    return render(request, 'piherz_store/contacto.html')

def sobre_nosotros(request):
    return render(request, 'piherz_store/sobre_nosotros.html')

def terminos_condiciones(request):
    return render(request, 'piherz_store/terminos_condiciones.html')

def politica_privacidad(request):
    return render(request, 'piherz_store/politica_privacidad.html')

def suscribir_newsletter(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        if email:
            if Newsletter.objects.filter(email=email).exists():
                messages.info(request, 'Este email ya está suscrito a nuestro newsletter')
            else:
                Newsletter.objects.create(email=email)
                messages.success(request, '¡Gracias por suscribirte a nuestro newsletter!')
        else:
            messages.error(request, 'Por favor ingresa un email válido')
    
    return redirect(request.META.get('HTTP_REFERER', 'index'))