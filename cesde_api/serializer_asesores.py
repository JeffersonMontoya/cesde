from rest_framework import serializers
from .models import *
from django.utils.dateparse import parse_date
from django.db.models import Sum, Count, Q

class ConsultaAsesoresSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=15)
    nombre_completo = serializers.SerializerMethodField()
    cantidad_llamadas = serializers.SerializerMethodField()
    cantidad_whatsapp = serializers.SerializerMethodField()
    cantidad_gestiones = serializers.SerializerMethodField()
    cantidad_matriculas = serializers.SerializerMethodField()
    cantidad_liquidaciones = serializers.SerializerMethodField()
    cantidad_gestiones_empresa = serializers.SerializerMethodField()
    cantidad_gestiones_tecnicos = serializers.SerializerMethodField()
    cantidad_gestiones_extensiones = serializers.SerializerMethodField()
    tiempo_promedio_whatsapp = serializers.SerializerMethodField()
    tiempo_promedio_llamada = serializers.SerializerMethodField()
    en_proceso_seleccion_llamadas = serializers.SerializerMethodField()
    en_proceso_seleccion_whatsapp = serializers.SerializerMethodField()
    

    class Meta:
        model = Asesores
        fields = [
            'id',
            'nombre_completo',
            'cantidad_llamadas',
            'cantidad_whatsapp',
            'cantidad_gestiones',
            'cantidad_matriculas',
            'cantidad_liquidaciones',
            'cantidad_gestiones_empresa',
            'cantidad_gestiones_tecnicos',
            'cantidad_gestiones_extensiones',
            'tiempo_promedio_whatsapp',
            'tiempo_promedio_llamada',
            'en_proceso_seleccion_llamadas',
            'en_proceso_seleccion_whatsapp',
        ]

    def get_nombre_completo(self, obj):
        return f"{obj.nombre_completo}".strip()

    def get_fecha_range(self):
        fecha_inicio = self.context['request'].query_params.get('fecha_inicio')
        fecha_fin = self.context['request'].query_params.get('fecha_fin')
        return fecha_inicio, fecha_fin

    def get_cantidad_llamadas(self, obj):
        fecha_inicio, fecha_fin = self.get_fecha_range()
        llamadas_gestion = Tipo_gestion.objects.filter(nombre='Llamada').first()
        if llamadas_gestion:
            query = Gestiones.objects.filter(asesor=obj, tipo_gestion=llamadas_gestion)
            if fecha_inicio:
                query = query.filter(fecha__gte=fecha_inicio)
            if fecha_fin:
                query = query.filter(fecha__lte=fecha_fin)
            return query.count()
        return 0

    def get_cantidad_whatsapp(self, obj):
        fecha_inicio, fecha_fin = self.get_fecha_range()
        whatsapp_gestion = Tipo_gestion.objects.filter(nombre='WhatsApp').first()
        if whatsapp_gestion:
            query = Gestiones.objects.filter(asesor=obj, tipo_gestion=whatsapp_gestion)
            if fecha_inicio:
                query = query.filter(fecha__gte=fecha_inicio)
            if fecha_fin:
                query = query.filter(fecha__lte=fecha_fin)
            return query.count()
        return 0

    def get_cantidad_gestiones(self, obj):
        fecha_inicio, fecha_fin = self.get_fecha_range()
        query = Gestiones.objects.filter(asesor=obj)
        if fecha_inicio:
            query = query.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            query = query.filter(fecha__lte=fecha_fin)
        return query.count()

    def get_cantidad_matriculas(self, obj):
        fecha_inicio, fecha_fin = self.get_fecha_range()
        matriculado_tipificacion = 'Matriculado'
        query = Gestiones.objects.filter(
            asesor=obj,
            tipificacion__nombre=matriculado_tipificacion
        )
        if fecha_inicio:
            query = query.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            query = query.filter(fecha__lte=fecha_fin)
        return query.distinct().count()

    def get_cantidad_liquidaciones(self, obj):
        fecha_inicio, fecha_fin = self.get_fecha_range()
        liquidado_tipificacion = 'Liquidacion'
        query = Gestiones.objects.filter(
            asesor=obj,
            tipificacion__nombre=liquidado_tipificacion
        )
        if fecha_inicio:
            query = query.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            query = query.filter(fecha__lte=fecha_fin)
        return query.distinct().count()

    # Esto es para saber las gestiones por separado de cada asesor por proceso
    def get_cantidad_gestiones_empresa(self, obj):
        return self._get_gestiones_por_proceso(obj, 'Empresas')

    def get_cantidad_gestiones_tecnicos(self, obj):
        return self._get_gestiones_por_proceso(obj, 'Técnicos')

    def get_cantidad_gestiones_extensiones(self, obj):
        return self._get_gestiones_por_proceso(obj, 'Extensiones')

    def _get_gestiones_por_proceso(self, obj, proceso_nombre):
        fecha_inicio, fecha_fin = self.get_fecha_range()
        query = Gestiones.objects.filter(asesor=obj, cel_aspirante__proceso__nombre=proceso_nombre)
        if fecha_inicio:
            query = query.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            query = query.filter(fecha__lte=fecha_fin)
        return query.count()
    
    def get_tiempo_promedio_whatsapp(self, obj):
        tipo_gestion = Tipo_gestion.objects.get(nombre='WhatsApp')
        query = Gestiones.objects.filter(asesor=obj, tipo_gestion_id=tipo_gestion)

        tiempo_segundos_total = sum(gestion.tiempo_gestion for gestion in query)
        total_gestiones = query.count()

        if total_gestiones == 0:
            return 0  # O el valor que consideres apropiado, como None o 'N/A'

        tiempo_minutos = tiempo_segundos_total / 60
        tiempo_promedio = tiempo_minutos / total_gestiones
        tiempo_promedio_redondeado = round(tiempo_promedio, 2)
        return tiempo_promedio_redondeado
    
    def get_tiempo_promedio_llamada(self, obj):
        tipo_gestion = Tipo_gestion.objects.get(nombre='Llamada')
        query = Gestiones.objects.filter(asesor=obj, tipo_gestion_id=tipo_gestion)
        
        tiempo_segundos_total = sum(gestion.tiempo_gestion for gestion in query)
        total_gestiones = query.count()
    
        if total_gestiones == 0:
            return 0 
        
        tiempo_minutos = tiempo_segundos_total / 60
        tiempo_promedio = tiempo_minutos / total_gestiones
        tiempo_promedio_redondeado = round(tiempo_promedio, 2)
        return tiempo_promedio_redondeado
    
    def get_en_proceso_seleccion_llamadas(self, obj):
        tipo_gestion = Tipo_gestion.objects.get(nombre='Llamada') 
        tipificacion = Tipificacion.objects.get(nombre='En_proceso_de_selección')

        query = Gestiones.objects.filter(asesor=obj, tipificacion=tipificacion, tipo_gestion_id=tipo_gestion)
        
        return query.count()
    
    def get_en_proceso_seleccion_whatsapp(self, obj):
        tipo_gestion = Tipo_gestion.objects.get(nombre='WhatsApp') 
        tipificacion = Tipificacion.objects.get(nombre='En_proceso_de_selección')
        
        query = Gestiones.objects.filter(asesor=obj, tipificacion=tipificacion, tipo_gestion_id=tipo_gestion)
        
        return query.count()
    
    