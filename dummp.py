
from constructapp.models import Standard_quality_materialCost
import os
import django
from django.conf import settings

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'constructmate.settings')
django.setup()

def populate_materials():
    standard_quality_material_Cost = [
        {'unit': 'cubic meters'},
        {'unit': 'liters'},
        {'unit': 'cubic meters'},
        {'unit': 'blocks'},
        {'unit': 'meters'},
        {'unit': 'meters'},
        {'unit': 'liters'},
        {'unit': 'pieces'},
        {'unit': 'cubic meters'},
        {'unit': 'kilograms'},
        {'unit': 'pieces'},
        {'unit': 'cubic meters'},
        {'unit': 'kilograms'},
        {'unit': 'cubic meters'}
    ]

    for material in standard_quality_material_Cost:
        Standard_quality_materialCost.objects.get_or_create(unit=material['unit'])

populate_materials()
