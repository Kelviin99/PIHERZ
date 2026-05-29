from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Esta línea controla el panel de administración
    path('admin/', admin.site.urls),
    
    # Esta línea conecta tu aplicación piherz_store
    path('', include('piherz_store.urls')),
]

# Configuración obligatoria para que carguen las fotos de tus productos en la web
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)