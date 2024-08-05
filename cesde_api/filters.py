from rest_framework import serializers
from .models import *
import django_filters
from django.db.models import Count, Q, Max
from django.utils import timezone
from datetime import timedelta

# Definición de los estados del aspirante
ESTADOS_CHOICES = [
        ('no gestionable', 'No Gestionable'),
        ('sin gestión', 'Sin Gestión'),
        ('en gestion', 'En Gestión'),
        ('cancelado', 'Cancelado'),
        ('liquidado', 'Liquidado'),
        ('matriculado', 'Matriculado'),
    ]

class AspirantesFilter(django_filters.FilterSet):
    cantidad_llamadas = django_filters.NumberFilter(method='filter_cantidad_llamadas', label='Cantidad de Llamadas')
    cantidad_mensajes_texto = django_filters.NumberFilter(method='filter_cantidad_mensajes_texto', label='Cantidad de Mensajes de Texto')
    cantidad_whatsapp = django_filters.NumberFilter(method='filter_cantidad_whatsapp', label='Cantidad de WhatsApp')
    cantidad_gestiones = django_filters.NumberFilter(method='filter_cantidad_gestiones', label='Cantidad de Gestiones')
    dias_ultima_gestion = django_filters.NumberFilter(method='filter_dias_ultima_gestion', label='Días Desde La Última Gestión')
    fecha_ultima_gestion = django_filters.DateFilter(method='filter_fecha_ultima_gestion', label='Fecha de Última Gestión')
    estado_aspirante = django_filters.ChoiceFilter(choices=ESTADOS_CHOICES, method='filter_estado_aspirante', label='Estado del Aspirante')
    sede = django_filters.ModelChoiceFilter(queryset=Sede.objects.all(), label='Sedes')
    nit_empresa = django_filters.NumberFilter(method='filter_nit_empresa', label='Nit Empresa')
    

    class Meta:   
        fields = [
            'cantidad_llamadas', 'cantidad_mensajes_texto', 'cantidad_whatsapp',
            'cantidad_gestiones', 'estado_aspirante', 'dias_ultima_gestion', 
            'fecha_ultima_gestion',  'sede' ,'nit_empresa' 
        ]


    def filter_cantidad_llamadas(self, queryset, name, value):
        llamadas_gestion = Tipo_gestion.objects.filter(nombre='Llamada').first()
        if llamadas_gestion:
            return queryset.annotate(
                cantidad_llamadas=Count('gestiones', filter=Q(gestiones__tipo_gestion=llamadas_gestion))
            ).filter(cantidad_llamadas=value) 
        return queryset


    def filter_cantidad_mensajes_texto(self, queryset, name, value):
        mensajes_texto_gestion = Tipo_gestion.objects.filter(nombre='SMS').first()
        if mensajes_texto_gestion:
            return queryset.annotate(
                cantidad_mensajes_texto=Count('gestiones', filter=Q(gestiones__tipo_gestion=mensajes_texto_gestion))
            ).filter(cantidad_mensajes_texto=value) 
        return queryset


    def filter_cantidad_whatsapp(self, queryset, name, value):
        whatsapp_gestion = Tipo_gestion.objects.filter(nombre='WhatsApp').first()
        if whatsapp_gestion:
            return queryset.annotate(
                cantidad_whatsapp=Count('gestiones', filter=Q(gestiones__tipo_gestion=whatsapp_gestion))
            ).filter(cantidad_whatsapp=value) 
        return queryset


    def filter_cantidad_gestiones(self, queryset, name, value):
        return queryset.annotate(
            cantidad_gestiones=Count('gestiones')
        ).filter(cantidad_gestiones=value) 


    def filter_estado_aspirante(self, queryset, name, value):
        return queryset.filter(estado__nombre=value)


    def filter_dias_ultima_gestion(self, queryset, name, value):
        if value:
            try:
                dias = int(value)
                fecha_limite = timezone.now().date() - timedelta(days=dias)

                # Anotar con la última fecha de gestión
                queryset = queryset.annotate(
                    dias_ultima_gestion=Max('gestiones__fecha')
                )

                # Filtrar aspirantes cuya última gestión sea exactamente hace el número de días especificado
                return queryset.filter(
                    dias_ultima_gestion__date=fecha_limite
                )
            except ValueError:
                return queryset.none()
        return queryset


    def filter_fecha_ultima_gestion(self, queryset, name, value):
        if value:
            fecha_limite = value

            # Anotar con la última fecha de gestión
            queryset = queryset.annotate(
                fecha_ultima_gestion=Max('gestiones__fecha')
            )

            # Comparar solo la parte de la fecha
            return queryset.filter(
                fecha_ultima_gestion__date=fecha_limite
            )
        return queryset


    def filter_nit_empresa(self, queryset, name, value):
        if value:
            return queryset.filter(empresa_nit_icontains=value)
        return queryset

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
    cel_aspirante = django_filters.CharFilter(field_name='cel_aspirante__celular', lookup_expr='icontains')
    fecha = django_filters.DateTimeFilter(field_name='fecha', lookup_expr='exact')
    tipo_gestion = django_filters.ModelChoiceFilter(queryset=Tipo_gestion.objects.all())
    observaciones = django_filters.CharFilter(lookup_expr='icontains')
    asesor = django_filters.ModelChoiceFilter(queryset=Asesores.objects.all())

    # Modelo y campos que se pueden filtrar
    class Meta:
        model = Gestiones
        fields = ['cel_aspirante', 'fecha', 'tipo_gestion', 'observaciones', 'asesor']
        
class SedeSerializer(serializers.ModelSerializer):
    sede = serializers.SerializerMethodField()
    
    class Meta:
        model = Sede
        fields = '__all__'


class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estados
        fields = ['nombre']
