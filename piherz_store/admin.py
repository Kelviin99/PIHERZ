# piherz_store/admin.py
from django.contrib import admin
from .models import Categoria, Producto, ImagenProducto, CarritoItem

class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 3
    fields = ['imagen', 'color', 'orden']
    ordering = ['orden']

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug']
    prepopulated_fields = {'slug': ('nombre',)}

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'stock', 'disponible', 'creado']
    list_filter = ['disponible', 'creado']
    list_editable = ['precio', 'stock', 'disponible']
    inlines = [ImagenProductoInline]

@admin.register(ImagenProducto)
class ImagenProductoAdmin(admin.ModelAdmin):
    list_display = ['producto', 'orden', 'creado']
    list_filter = ['creado']
    ordering = ['producto', 'orden']

@admin.register(CarritoItem)
class CarritoItemAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'producto', 'cantidad', 'creado', 'actualizado']
    list_filter = ['creado', 'actualizado']
    search_fields = ['usuario__username', 'producto__nombre']
    readonly_fields = ['creado', 'actualizado']
