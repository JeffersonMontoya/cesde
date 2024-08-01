# cesde/filters.py
import django_filters
from .models import *

class AspirantesFilter(django_filters.FilterSet): # Define un conjunto de filtros para un modelo especifico
    #Filtros por cada campo
    nombre = django_filters.CharFilter(lookup_expr='icontains') 
    correo = django_filters.CharFilter(lookup_expr='icontains')
    documento = django_filters.CharFilter(lookup_expr='icontains')
    celular = django_filters.CharFilter(lookup_expr='icontains')
    ciudad = django_filters.ModelChoiceFilter(queryset=Ciudad.objects.all()) #ModelChoiceFilter permite filtrar por relaciones de clave forenea
    estado = django_filters.ModelChoiceFilter(queryset=Estados.objects.all())
    programa = django_filters.ModelChoiceFilter(queryset=Programa.objects.all())
    empresa = django_filters.ModelChoiceFilter(queryset=Empresa.objects.all())


    # Modelo y campos que se pueden filtrar
    class Meta:
        model = Aspirantes
        fields = ['nombre', 'correo', 'documento', 'celular', 'ciudad', 'estado', 'programa', 'empresa' ]


class DepartamentosFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(lookup_expr='icontains')

    # Modelo y campos que se pueden filtrar
    class Meta:
        model = Departamento
        fields = ['nombre']


class CiudadesFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(lookup_expr='icontains')
    departamento = django_filters.ModelChoiceFilter(queryset=Departamento.objects.all())

    class Meta:
        model = Ciudad
        fields = ['nombre', 'departamento']


class EstadosFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(lookup_expr='icontains')

    # Modelo y campos que se pueden filtrar
    class Meta:
        model = Estados
        fields = ['nombre']


class ProgramaFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(lookup_expr='icontains')
    descripcion = django_filters.CharFilter(lookup_expr='icontains')

    # Modelo y campos que se pueden filtrar
    class Meta:
        model = Programa
        fields = ['nombre', 'descripcion']


class EmpresaFilter(django_filters.FilterSet):
    nit = django_filters.CharFilter(lookup_expr='icontains')

    # Modelo y campos que se pueden filtrar
    class Meta: 
        model = Empresa
        fields = ['nit']


class Tipo_gestionFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(lookup_expr='icontains')

    # Modelo y campos que se pueden filtrar
    class Meta:
        model = Tipo_gestion
        fields = ['nombre']


class AsesoresFilter(django_filters.FilterSet):
    documento = django_filters.CharFilter(lookup_expr='icontains')

    # Modelo y campos que se pueden filtrar
    class Meta:
        model = Asesores
        fields = ['documento']

class GestionesFilter(django_filters.FilterSet):
    cel_aspirante = django_filters.ModelChoiceFilter(queryset=Aspirantes.objects.all())
    fecha = django_filters.DateTimeFilter(field_name='fecha', lookup_expr='exact')
    tipo_gestion = django_filters.ModelChoiceFilter(queryset=Tipo_gestion.objects.all())
    observaciones = django_filters.CharFilter(lookup_expr='icontains')
    asesor = django_filters.ModelChoiceFilter(queryset=Asesores.objects.all())

    # Modelo y campos que se pueden filtrar
    class Meta:
        model = Gestiones
        fields = ['cel_aspirante', 'fecha', 'tipo_gestion', 'observaciones', 'asesor']








