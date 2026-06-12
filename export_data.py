import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'piherz_project.settings')
django.setup()

from django.core.management import call_command

# Exportar datos a JSON con codificación UTF-8
with open('datos.json', 'w', encoding='utf-8') as f:
    call_command('dumpdata', indent=2, stdout=f)

print("Archivo datos.json creado exitosamente con codificación UTF-8")
