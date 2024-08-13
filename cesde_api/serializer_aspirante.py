from rest_framework import serializers
from .models import *
from datetime import datetime


class AspiranteSerializer(serializers.ModelSerializer):
    nit = serializers.CharField(source='documento')
    nombre_completo = serializers.SerializerMethodField()
    cantidad_llamadas = serializers.SerializerMethodField()
    cantidad_whatsapp = serializers.SerializerMethodField()
    cantidad_gestiones = serializers.SerializerMethodField()
    fecha_ultima_gestion = serializers.SerializerMethodField()
    dias_ultima_gestion = serializers.SerializerMethodField()
    sede = serializers.CharField(source='sede.nombre')
    estado_ultima_gestion = serializers.SerializerMethodField()
    estado_aspirante = serializers.CharField(source='estado.nombre')
    programa_formacion = serializers.CharField(source='programa.nombre')
    patrocinio_empresa = serializers.CharField(source='empresa.nit')
    proceso = serializers.CharField(source='proceso.nombre')


    class Meta:
        model = Aspirantes
        fields = [
            'nombre_completo',
            'nit', 
            'estado_aspirante', 
            'sede',  
            'patrocinio_empresa', 
            'programa_formacion', 
            'proceso',
            'celular',
            'cantidad_llamadas',  
            'cantidad_whatsapp', 
            'cantidad_gestiones',
            'fecha_ultima_gestion', 
            'dias_ultima_gestion', 
            'estado_ultima_gestion'
        ]



    # Funcion para traer el nombre completo del aspirante
    def get_nombre_completo(self, obj):
        return obj.nombre

    # Funcion para llevar el conteo de llamadas del aspirante

    def get_cantidad_llamadas(self, obj):
        llamadas_gestion = Tipo_gestion.objects.filter(
            nombre='Llamada').first()
        if llamadas_gestion:
            return Gestiones.objects.filter(cel_aspirante=obj, tipo_gestion=llamadas_gestion).count()
        return 0

    def get_cantidad_whatsapp(self, obj):
        whatsapp_gestion = Tipo_gestion.objects.filter(
            nombre='WhatsApp').first()

        # Filtramos el modelo Gestiones para contar todas las gestiones asociadas al aspirante actual (obj) y que tengan el tipo de gestión encontrado (llamadas_gestion). count() devuelve el número de estas gestiones.
        if whatsapp_gestion:
            return Gestiones.objects.filter(cel_aspirante=obj, tipo_gestion=whatsapp_gestion).count()
        return 0

    # Funcion para llevar el conteo  de gestiones

    def get_cantidad_gestiones(self, obj):
        cantidad_gestiones = Gestiones.objects.filter(
            cel_aspirante=obj).count()
        return cantidad_gestiones

    # Función para obtener la fecha de la última gestión del celular adicional oeee
    def get_fecha_ultima_gestion(self, obj):
        ultima_gestion = Gestiones.objects.filter(
            cel_aspirante=obj, fecha__isnull=False).order_by('-fecha').first()
        if ultima_gestion:
        # Formatear la fecha para que solo devuelva año, mes y día
            return ultima_gestion.fecha.strftime('%Y-%m-%d')
        return None

    def get_estado_ultima_gestion(self, obj):
        ultima_gestion = Gestiones.objects.filter(
            cel_aspirante=obj, fecha__isnull=False).order_by('-fecha').first()
        if ultima_gestion:
            # El estado de la última gestión se obtiene de la tipificación relacionada
            return ultima_gestion.tipificacion.nombre
        return None

    def get_dias_ultima_gestion(self, obj):
        ultima_gestion = Gestiones.objects.filter(
            cel_aspirante=obj,
            fecha__isnull=False
        ).order_by('-fecha').first()
        if ultima_gestion:
            fecha_ultima = ultima_gestion.fecha.date() if isinstance(
                ultima_gestion.fecha, datetime) else ultima_gestion.fecha
            delta = datetime.now().date() - fecha_ultima
            return delta.days
        return None
