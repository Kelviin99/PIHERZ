# piherz_store/carrito.py

class Carrito:
    def __init__(self, request):
        """Inicializa el carrito de compras usando las sesiones de Django"""
        self.session = request.session
        carrito = self.session.get('carrito')
        if not carrito:
            # Si el cliente no tiene un carrito activo, le creamos uno vacío
            carrito = self.session['carrito'] = {}
        self.carrito = carrito

    def agregar(self, producto, cantidad=1):
        """Añade un producto al carrito de piherz o actualiza su cantidad"""
        producto_id = str(producto.id)
        if producto_id not in self.carrito:
            self.carrito[producto_id] = {
                'precio': str(producto.precio),
                'cantidad': 0
            }
        self.carrito[producto_id]['cantidad'] += cantidad
        self.guardar()

    def guardar(self):
        """Marca la sesión como modificada para que se guarde en el navegador"""
        self.session.modified = True

    def quitar(self, producto):
        """Elimina un producto por completo del carrito"""
        producto_id = str(producto.id)
        if producto_id in self.carrito:
            del self.carrito[producto_id]
            self.guardar()