from rest_framework import serializers
from .models import Gestiones, Asesores

class HistoricoGestionesSerializer(serializers.ModelSerializer):
    tipo_gestion_nombre = serializers.SerializerMethodField()
    tipificacion_nombre = serializers.SerializerMethodField()
    nombre_completo_aspirante = serializers.SerializerMethodField()
    asesor = serializers.SerializerMethodField()
    sede_nombre = serializers.SerializerMethodField()
    programa_nombre = serializers.SerializerMethodField()
    empresa_aspirante = serializers.CharField(source='empresa')
    tiempo_gestion = serializers.SerializerMethodField()

    class Meta:
        model = Gestiones
        fields = ['nombre_completo_aspirante', 'cel_aspirante', 'fecha', 'tipo_gestion_nombre', 'observaciones',
                    'tipificacion_nombre', 'asesor', 'sede_nombre', 'programa_nombre', 'empresa_aspirante', 'tiempo_gestion']

    def get_asesor(self, obj):
        return obj.asesor.nombre_completo

    def get_tipo_gestion_nombre(self, obj):
        return obj.tipo_gestion.nombre if obj.tipo_gestion else None

    def get_tipificacion_nombre(self, obj):
        return obj.tipificacion.nombre if obj.tipificacion else None

    def get_nombre_completo_aspirante(self, obj):
        # Asumiendo que `cel_aspirante` es una relación con el modelo `Aspirantes`
        aspirante = obj.cel_aspirante
        if aspirante:
            return aspirante.nombre
        return None
    
    def get_sede_nombre(self, obj):
        # Asumiendo que `cel_aspirante` es una relación con el modelo `Aspirantes`
        aspirante = obj.cel_aspirante
        return aspirante.sede.nombre if aspirante and aspirante.sede else None

    def get_programa_nombre(self, obj):
        # Asumiendo que `cel_aspirante` es una relación con el modelo `Aspirantes`
        aspirante = obj.cel_aspirante
        return aspirante.programa.nombre if aspirante and aspirante.programa else None

    def get_tiempo_gestion(self, obj):
        tiempo_gestion = obj.tiempo_gestion
        return tiempo_gestion