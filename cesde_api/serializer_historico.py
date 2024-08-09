
from rest_framework import serializers
from .models import Gestiones

class HistoricoGestionesSerializer(serializers.ModelSerializer):
    tipo_gestion_nombre = serializers.SerializerMethodField()
    tipificacion_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Gestiones
        fields = ['id', 'cel_aspirante', 'fecha', 'tipo_gestion', 'tipo_gestion_nombre', 'observaciones', 'tipificacion', 'tipificacion_nombre', 'asesor']

    def get_tipo_gestion_nombre(self, obj):
        return obj.tipo_gestion.nombre if obj.tipo_gestion else None

    def get_tipificacion_nombre(self, obj):
        return obj.tipificacion.nombre if obj.tipificacion else None
