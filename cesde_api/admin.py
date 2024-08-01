from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register([Departamento, Ciudad, Estados, Aspirantes, Tipo_gestion, Asesores , Gestiones , Programa , Empresa , Proceso , Tipificacion])
