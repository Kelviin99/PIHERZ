# piherz_store/carrito.py
from .models import CarritoItem

class Carrito:
    def __init__(self, request):
        """Inicializa el carrito de compras usando sesiones o base de datos"""
        self.request = request
        self.usuario = request.user if request.user.is_authenticated else None
        
        if self.usuario:
            # Usuario autenticado: usar base de datos
            self._cargar_carrito_db()
        else:
            # Usuario no autenticado: usar sesión
            self.session = request.session
            carrito = self.session.get('carrito')
            if not carrito:
                carrito = self.session['carrito'] = {}
            self.carrito = carrito

    def _cargar_carrito_db(self):
        """Carga el carrito desde la base de datos para usuarios autenticados"""
        from .models import CarritoItem
        carrito_items = CarritoItem.objects.filter(usuario=self.usuario)
        self.carrito = {}
        for item in carrito_items:
            self.carrito[str(item.producto.id)] = {
                'precio': str(item.producto.precio),
                'cantidad': item.cantidad,
                'db_item': item  # Referencia al item de base de datos
            }

    def agregar(self, producto, cantidad=1):
        """Añade un producto al carrito o actualiza su cantidad"""
        if self.usuario:
            # Usuario autenticado: usar base de datos
            self._agregar_db(producto, cantidad)
        else:
            # Usuario no autenticado: usar sesión
            self._agregar_sesion(producto, cantidad)

    def _agregar_db(self, producto, cantidad):
        """Agrega producto al carrito en base de datos"""
        producto_id = str(producto.id)
        carrito_item, created = CarritoItem.objects.get_or_create(
            usuario=self.usuario,
            producto=producto,
            defaults={'cantidad': cantidad}
        )
        if not created:
            carrito_item.cantidad += cantidad
            carrito_item.save()
        
        # Actualizar el carrito en memoria
        if producto_id not in self.carrito:
            self.carrito[producto_id] = {
                'precio': str(producto.precio),
                'cantidad': 0
            }
        self.carrito[producto_id]['cantidad'] += cantidad
        self.carrito[producto_id]['db_item'] = carrito_item

    def _agregar_sesion(self, producto, cantidad):
        """Agrega producto al carrito en sesión"""
        producto_id = str(producto.id)
        if producto_id not in self.carrito:
            self.carrito[producto_id] = {
                'precio': str(producto.precio),
                'cantidad': 0
            }
        self.carrito[producto_id]['cantidad'] += cantidad
        self.guardar()

    def guardar(self):
        """Marca la sesión como modificada"""
        if not self.usuario:
            self.session.modified = True

    def quitar(self, producto):
        """Elimina un producto por completo del carrito"""
        if self.usuario:
            # Usuario autenticado: eliminar de base de datos
            self._quitar_db(producto)
        else:
            # Usuario no autenticado: eliminar de sesión
            self._quitar_sesion(producto)

    def _quitar_db(self, producto):
        """Elimina producto del carrito en base de datos"""
        producto_id = str(producto.id)
        CarritoItem.objects.filter(usuario=self.usuario, producto=producto).delete()
        if producto_id in self.carrito:
            del self.carrito[producto_id]

    def _quitar_sesion(self, producto):
        """Elimina producto del carrito en sesión"""
        producto_id = str(producto.id)
        if producto_id in self.carrito:
            del self.carrito[producto_id]
            self.guardar()

    def limpiar(self):
        """Limpia el carrito completo"""
        if self.usuario:
            # Usuario autenticado: eliminar todos los items de base de datos
            CarritoItem.objects.filter(usuario=self.usuario).delete()
            self.carrito = {}
        else:
            # Usuario no autenticado: limpiar sesión
            self.session['carrito'] = {}
            self.carrito = {}
            self.guardar()