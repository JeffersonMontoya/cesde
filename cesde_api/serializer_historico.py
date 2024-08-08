from rest_framework import serializers
from .models import Gestiones

class HistoricoSerializer(serializers.ModelSerializer):
    fechas_gestiones_por_aspirante = serializers.SerializerMethodField()

    class Meta:
        model = Gestiones
        fields = ['fechas_gestiones_por_aspirante']

    def get_fechas_gestiones_por_aspirante(self, obj):
        celular = self.context['request'].query_params.get('celular_aspirante')
        if celular:
            gestiones = Gestiones.objects.filter(cel_aspirante__celular=celular).order_by('fecha')
        else:
            gestiones = Gestiones.objects.none()  # Retornar vacío si no se proporciona celular

        return [
            {
                'nombre_completo': f"{gestion.cel_aspirante.nombre} {gestion.cel_aspirante.apellidos}",
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
