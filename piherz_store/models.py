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