from rest_framework import serializers
from .models import *

class HistoricoSerializer(serializers.ModelSerializer):
    fechas_gestiones_por_aspirante = serializers.SerializerMethodField()

    class Meta:
        model = Gestiones
        fields = ['fechas_gestiones_por_aspirante']

    def get_fechas_gestiones_por_aspirante(self, obj):
        gestiones = Gestiones.objects.filter(cel_aspirante=obj).order_by('fecha')
        return [
            {
                'nombre_completo': gestion.cel_aspirante.nombre,
                'celular': gestion.cel_aspirante.celular,
                'fecha': gestion.fecha,
                'asesor': gestion.asesor.nombre_completo,
                'descripcion': gestion.observaciones,
                'tipo_gestion': gestion.tipo_gestion.nombre,
                'resultado_gestion': gestion.tipificacion.nombre,
                'programa': gestion.cel_aspirante.programa.nombre,
                'sede': gestion.cel_aspirante.sede.nombre
            }
            for gestion in gestiones
        ]
