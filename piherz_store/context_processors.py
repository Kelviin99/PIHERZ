# piherz_store/context_processors.py
from .carrito import Carrito

def carrito_context(request):
    """Context processor para hacer disponible el carrito en todos los templates"""
    carrito_obj = Carrito(request)
    carrito_cantidad = sum(item['cantidad'] for item in carrito_obj.carrito.values())
    return {
        'carrito_cantidad': carrito_cantidad,
    }
