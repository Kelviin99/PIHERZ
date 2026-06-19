from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    titulo_largo = models.CharField(max_length=200, blank=True, help_text='Título largo para mostrar en la página de detalle (ej: "Chaqueta para todo tipo de moto")')
    precio = models.DecimalField(max_digits=10, decimal_places=0) # Configurado para pesos colombianos
    stock = models.IntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    disponible = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='productos/')
    color = models.CharField(max_length=50, blank=True, help_text='Color de esta variante (ej: Negro, Azul, Gris)')
    orden = models.IntegerField(default=0)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['orden', 'creado']

    def __str__(self):
        color_str = f" - {self.color}" if self.color else ""
        return f"Imagen de {self.producto.nombre}{color_str}"

class CarritoItem(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carrito_items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('usuario', 'producto')
        ordering = ['-creado']

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} ({self.usuario.username})"

    def subtotal(self):
        return self.cantidad * self.producto.precio

class Direccion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='direcciones')
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=20)
    telefono = models.CharField(max_length=20)
    es_predeterminada = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-es_predeterminada', '-creado']

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.ciudad}"

    def direccion_completa(self):
        return f"{self.direccion}, {self.ciudad}, {self.departamento}, {self.codigo_postal}"

class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    numero_pedido = models.CharField(max_length=50, unique=True)
    direccion = models.ForeignKey(Direccion, on_delete=models.SET_NULL, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    subtotal = models.DecimalField(max_digits=10, decimal_places=0)
    costo_envio = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=0)
    notas = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creado']

    def __str__(self):
        return f"Pedido #{self.numero_pedido} - {self.usuario.username}"

    def save(self, *args, **kwargs):
        if not self.numero_pedido:
            self.numero_pedido = self.generar_numero_pedido()
        super().save(*args, **kwargs)

    def generar_numero_pedido(self):
        import random
        import string
        from datetime import datetime
        fecha = datetime.now().strftime('%Y%m%d')
        random_str = ''.join(random.choices(string.digits, k=6))
        return f"PIH-{fecha}-{random_str}"

class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    nombre_producto = models.CharField(max_length=200)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=0)
    cantidad = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=0)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.cantidad} x {self.nombre_producto}"

    def save(self, *args, **kwargs):
        self.subtotal = self.precio_unitario * self.cantidad
        super().save(*args, **kwargs)

class Reseña(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='resenas')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    calificacion = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comentario = models.TextField()
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('producto', 'usuario')
        ordering = ['-creado']

    def __str__(self):
        return f"{self.usuario.username} - {self.producto.nombre} ({self.calificacion}/5)"

class ListaDeseos(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lista_deseos')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'producto')
        ordering = ['-creado']

    def __str__(self):
        return f"{self.usuario.username} - {self.producto.nombre}"

class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado']

    def __str__(self):
        return self.email