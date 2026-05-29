# 📸 Galería de Múltiples Imágenes - Guía de Uso

## ✅ Lo que se implementó:

### 1. **Galería Interactiva de Imágenes** ✨
   - Los recuadros pequeños (thumbnails) ahora son **clickeables**
   - Al hacer clic en un recuadro, la imagen grande cambia automáticamente
   - El recuadro seleccionado se resalta en color **CYAN** con fondo claro
   - **Hover effect**: Al pasar el mouse sobre un thumbnail se resalta el borde

### 2. **Sistema de Múltiples Imágenes por Producto**
   - Cada producto puede tener hasta **4+ imágenes adicionales**
   - Las imágenes se ordenan automáticamente por el campo "Orden"
   - Sistema totalmente compatible con la estructura actual

### 3. **Panel de Administración Mejorado**
   - Interfaz inline para agregar imágenes directamente en el producto
   - Campo `Orden` para controlar la secuencia de las imágenes
   - Posibilidad de agregar hasta 3 imágenes por defecto (se pueden agregar más)

---

## 🚀 CÓMO USAR - Paso a Paso:

### **Opción 1: Acceder desde Panel Admin**

#### Paso 1: Entrar al Panel de Administración
```
http://127.0.0.1:8000/admin/
```

#### Paso 2: Seleccionar un Producto
- Ir a **Piherz_store → Productos**
- Hacer clic en el producto que deseas editar (ej: Chaqueta)

#### Paso 3: Agregar las Imágenes
- **Bajar hasta la sección**: "Imagenes de producto"
- **Hacer clic en**: "Agregar otra fila" para cada imagen que quieras agregar
- **Seleccionar la imagen**: Usar el botón de explorar para elegir el archivo
- **Asignar orden** (muy importante):
  - **0** = Primera imagen (aparece al cargar la página)
  - **1** = Segunda imagen
  - **2** = Tercera imagen
  - **3+** = Sucesivamente

#### Paso 4: Guardar
- Hacer clic en **"Guardar"** al final de la página

### **Opción 2: Desde la Línea de Comandos (Avanzado)**

Si prefieres agregar imágenes por código:
```python
from piherz_store.models import Producto, ImagenProducto

# Obtener el producto
producto = Producto.objects.get(nombre='Chaqueta')

# Agregar imágenes
ImagenProducto.objects.create(
    producto=producto,
    imagen='productos/imagen1.jpg',
    orden=0
)
ImagenProducto.objects.create(
    producto=producto,
    imagen='productos/imagen2.jpg',
    orden=1
)
```

---

## 🎯 Cómo se Ve en la Tienda:

Cuando el cliente visitaun producto:

✅ **Verá:**
- Recuadros pequeños a la izquierda con las imágenes
- Imagen grande en el centro

✅ **Al pasar el mouse:**
- El cursor cambia a pointer
- El recuadro se resalta ligeramente

✅ **Al hacer clic:**
- La imagen grande se actualiza a la seleccionada
- El recuadro se resalta en **CYAN** con fondo claro
- Transición suave de 0.3 segundos

---

## 📁 Archivos Modificados:

1. **models.py**: Nuevo modelo `ImagenProducto`
2. **admin.py**: Interfaz inline para gestionar imágenes
3. **detalle.html**: Template actualizado con galería interactiva
4. **style.css**: Estilos para los thumbnails
5. **migrations/0002_imagenproducto.py**: Migración de base de datos

---

## ⚡ Notas Técnicas:

| Característica | Detalles |
|---|---|
| **Almacenamiento** | `media/productos/` |
| **Base de datos** | `db.sqlite3` (tabla `ImagenProducto`) |
| **Compatibilidad** | Si no hay imágenes adicionales, muestra la imagen principal 4 veces |
| **Respuesta** | Galería NO responsiva en mobile (solo en desktop) |
| **JavaScript** | Función `cambiarImagen()` con soporte para clic |
| **CSS** | Transiciones suaves y efectos de hover |

---

## 🔧 Solución de Problemas:

### ❌ Las imágenes no aparecen:
- Verifica que las imágenes estén en la carpeta `media/productos/`
- Revisa que el permiso de lectura sea correcto
- Reinicia el servidor con `python manage.py runserver`

### ❌ No se ve el resaltado al hacer clic:
- Limpia el cache del navegador (Ctrl+Shift+Delete)
- Verifica que los archivos CSS se hayan cargado correctamente
- Abre la consola (F12) y busca errores

### ❌ Los thumbnails no cambian la imagen:
- Verifica que la URL de la imagen sea correcta
- Abre la consola (F12) para ver si hay errores JavaScript

---

## 💡 Tips:

- **Orden 0 es importante**: Asegúrate de que la primera imagen tenga orden 0
- **Nombres descriptivos**: Usa nombres claros para tus imágenes
- **Calidad de imagen**: Las imágenes deben ser de buena calidad
- **Tamaño recomendado**: 600x600px o mayor
- **Formato**: JPG o PNG funcionan bien

---

**¡La galería ya está lista para usar!** 🎉

Ahora puedes hacer que tus productos luzcan increíbles con múltiples imágenes. 📸

