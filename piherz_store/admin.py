# piherz_store/admin.py
from django.contrib import admin
from .models import Categoria, Producto, ImagenProducto

class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 3
    fields = ['imagen', 'orden']
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
