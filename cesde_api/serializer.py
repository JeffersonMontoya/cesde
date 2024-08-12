from rest_framework import serializers
from .models import *
from datetime import datetime

from .models import *


class SedeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sede
        fields = '__all__'


class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estados
        fields = ['nombre']



    class Meta:
        model = Aspirantes
        fields = [
            'nit', 'celular', 'nombre_completo', 'cantidad_llamadas',
            'cantidad_mensajes_texto', 'cantidad_whatsapp', 'cantidad_gestiones',
            'fecha_ultima_gestion' , 'celular_adicional'
        ]
        #    Funcion para traer el celular adicional

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

    def get_cantidad_mensajes_texto(self, obj):
        mensajes_texto_gestion = Tipo_gestion.objects.filter(
            nombre='SMS').first()
        if mensajes_texto_gestion:
            return Gestiones.objects.filter(cel_aspirante=obj, tipo_gestion=mensajes_texto_gestion).count()
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
    
    
    # Función para obtener la fecha de la última gestión del celular adicional
    def get_fecha_ultima_gestion(self, obj):
        ultima_gestion = Gestiones.objects.filter(
            cel_aspirante=obj, fecha__isnull=False).order_by('-fecha').first()
        if ultima_gestion:
            return ultima_gestion.fecha
        return None

    def get_estado_ultima_gestion(self, obj):
        ultima_gestion = Gestiones.objects.filter(
            cel_aspirante=obj, fecha__isnull=False).order_by('-fecha').first()
        if ultima_gestion:
            # El estado de la última gestión se obtiene de la tipificación relacionada
            return ultima_gestion.tipificacion.nombre
        return None

class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estados
        fields = '__all__'


class TipoGestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tipo_gestion
        fields = '__all__'


class GestionSerializer(serializers.ModelSerializer):
    tipo_gestion = serializers.SerializerMethodField()
    tipificacion = serializers.SerializerMethodField()
    asesor = serializers.SerializerMethodField()  # Agrega el campo para el asesor

    class Meta:
        model = Gestiones
        fields = ['cel_aspirante', 'fecha', 'tipo_gestion',
                'observaciones', 'tipificacion','asesor']

    def get_tipo_gestion(self, obj):
        return obj.tipo_gestion.nombre

    def get_tipificacion(self, obj):
        return obj.tipificacion.nombre

    def get_asesor(self, obj):
        # Retorna la información del asesor, puedes ajustar el campo retornado si es necesario
        if obj.asesor:
            return {
                'id': obj.asesor.id,
                'nombre_completo': obj.asesor.nombre_completo
            }
        return None


class ProgramaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Programa
        fields = '__all__'


class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = '__all__'


class ProcesoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proceso
        fields = '__all__'


class TipificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tipificacion
        fields = '__all__'




class AsesorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asesores
        fields = '__all__'
