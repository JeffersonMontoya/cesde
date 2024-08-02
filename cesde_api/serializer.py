from rest_framework import serializers
from .models import (
    Aspirantes, Gestiones, Tipo_gestion, Estados,
     Asesores, Programa,
    Empresa, Proceso, Tipificacion , Sede
)


class SedeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Sede
        fields ='__all__'


class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estados
        fields = ['nombre']

class AspiranteSerializer(serializers.ModelSerializer):
    nit = serializers.CharField(source='documento')
    nombre_completo = serializers.SerializerMethodField()
    cantidad_llamadas = serializers.SerializerMethodField()
    cantidad_mensajes_texto = serializers.SerializerMethodField()
    cantidad_whatsapp = serializers.SerializerMethodField()
    cantidad_gestiones = serializers.SerializerMethodField()
    celular_adicional = serializers.CharField(source='cel_opcional')
    fecha_ultima_gestion = serializers.SerializerMethodField()
    estado_ultima_gestion = serializers.SerializerMethodField()
    estado_aspirante = serializers.CharField(source='estado.nombre')

    class Meta:
        model = Aspirantes
        fields = [
            'nit', 'celular', 'nombre_completo', 'cantidad_llamadas',
            'cantidad_mensajes_texto', 'cantidad_whatsapp', 'cantidad_gestiones',
            'celular_adicional', 'fecha_ultima_gestion', 'estado_ultima_gestion',
            'estado_aspirante',
        ]

    def get_nombre_completo(self, obj):
        return f"{obj.nombre} {obj.apellidos}"

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
            nombre='Whatsapp').first()
        if whatsapp_gestion:
            return Gestiones.objects.filter(cel_aspirante=obj, tipo_gestion=whatsapp_gestion).count()
        return 0

    def get_cantidad_gestiones(self, obj):
        return Gestiones.objects.filter(cel_aspirante=obj).count()

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

class TipoGestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tipo_gestion
        fields = ['nombre']

class AsesorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asesores
        fields = ['documento', 'nombre', 'apellido']

class GestionSerializer(serializers.ModelSerializer):
    tipo_gestion = serializers.SerializerMethodField()
    tipificacion = serializers.SerializerMethodField()

    class Meta:
        model = Gestiones
        fields = ['cel_aspirante', 'fecha', 'tipo_gestion', 'observaciones', 'tipificacion']

    def get_tipo_gestion(self, obj):
        return obj.tipo_gestion.nombre

    def get_tipificacion(self, obj):
        return obj.tipificacion.nombre

class ProgramaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Programa
        fields = ['nombre', 'descripcion']

class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = ['nit']

class ProcesoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proceso
        fields = ['nombre']

class TipificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tipificacion
        fields = ['nombre']
        
        
