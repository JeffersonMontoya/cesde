from rest_framework import serializers
from datetime import datetime
from .models import *


class AspiranteFilterSerializer(serializers.ModelSerializer):
    nit = serializers.CharField(source='documento')
    nombre_completo = serializers.SerializerMethodField()
    cantidad_llamadas = serializers.SerializerMethodField()
    cantidad_whatsapp = serializers.SerializerMethodField()
    cantidad_gestiones = serializers.SerializerMethodField()
    dias_ultima_gestion = serializers.SerializerMethodField()
    fecha_ultima_gestion = serializers.SerializerMethodField()
    tipificacion = serializers.SerializerMethodField()
    programa = serializers.CharField(source='programa.nombre') 
    sede = serializers.CharField(source='sede.nombre')
    nit_empresa = serializers.CharField(source='empresa.nit')
    proceso = serializers.CharField(source='proceso.nombre')
    estado_ultima_gestion = serializers.SerializerMethodField()

    class Meta:
        model = Aspirantes
        fields = [
            'nit', 
            'celular',
            'nombre_completo',
            'cantidad_llamadas',
            'cantidad_whatsapp',
            'cantidad_gestiones', 
            'tipificacion', 
            'dias_ultima_gestion', 
            'fecha_ultima_gestion',
            'programa', 
            'sede', 
            'nit_empresa', 
            'proceso',
            'estado_ultima_gestion', 
        ]


    def get_nombre_completo(self, obj):
        return obj.nombre


    def get_cantidad_llamadas(self, obj):
        llamadas_gestion = Tipo_gestion.objects.filter(nombre='Llamada').first()
        if llamadas_gestion:
            return Gestiones.objects.filter(cel_aspirante=obj, tipo_gestion=llamadas_gestion).count()
        return 0


    def get_cantidad_whatsapp(self, obj):
        whatsapp_gestion = Tipo_gestion.objects.filter(nombre='WhatsApp').first()
        if whatsapp_gestion:
            return Gestiones.objects.filter(cel_aspirante=obj, tipo_gestion=whatsapp_gestion).count()
        return 0


    def get_cantidad_gestiones(self, obj):
        return Gestiones.objects.filter(cel_aspirante=obj).count()


    def get_tipificacion(self, obj):
        ultima_gestion = Gestiones.objects.filter(cel_aspirante=obj).order_by('-fecha').first()
        if ultima_gestion:
            return ultima_gestion.tipificacion.nombre
        return None


    def get_dias_ultima_gestion(self, obj):
        ultima_gestion = Gestiones.objects.filter(
            cel_aspirante=obj,
            fecha__isnull=False
        ).order_by('-fecha').first()
        if ultima_gestion:
            fecha_ultima = ultima_gestion.fecha.date() if isinstance(ultima_gestion.fecha, datetime) else ultima_gestion.fecha
            delta = datetime.now().date() - fecha_ultima
            return delta.days
        return None


    # Función para obtener la fecha de la última gestión del celular adicional oeee
    def get_fecha_ultima_gestion(self, obj):
        ultima_gestion = Gestiones.objects.filter(
             cel_aspirante=obj, fecha__isnull=False).order_by('-fecha').first()
    
        if ultima_gestion:
        # Formatear la fecha para que solo devuelva año, mes y día
            return ultima_gestion.fecha.strftime('%Y-%m-%d')
    
        # Si no hay gestiones, retornar un mensaje específico
        return None
    
    
        # Función para obtener el estado de la última gestión del celular adicional
    def get_estado_ultima_gestion(self, obj):
        ultima_gestion = Gestiones.objects.filter(
            cel_aspirante=obj
        ).order_by('-fecha').first()
        if ultima_gestion:
        # Asumiendo que el estado está relacionado con la gestión y tiene un campo accesible
            return ultima_gestion.estado.nombre  # Cambia 'estado.nombre' según tu estructura de modelo
        return  None