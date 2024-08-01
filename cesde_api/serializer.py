from .models import Aspirantes, Gestiones, Tipo_gestion, Estados
from .models import Gestiones, Tipo_gestion, Estados
from rest_framework import serializers
from .models import *


class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = '__all__'


class CiudadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ciudad
        fields = '__all__'


class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estados
        fields = '__all__'



class AspiranteSerializer(serializers.ModelSerializer):
    nit = serializers.CharField(source='documento')
    nombre_completo = serializers.SerializerMethodField()
    cantidad_llamadas = serializers.SerializerMethodField()
    cantidad_mensajes_texto = serializers.SerializerMethodField()
    cantidad_whatsapp = serializers.SerializerMethodField()
    cantidad_gestiones = serializers.SerializerMethodField()
    fecha_ultima_gestion = serializers.SerializerMethodField()
    celular_adicional = serializers.CharField(source='cel_opcional')

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
        return f"{obj.nombre} {obj.apellidos}"
    

    
    
    # Funcion para llevar el conteo de llamadas del aspirante
    def get_cantidad_llamadas(self, obj):
        # Se busca el primer objeto en Tipo_gestion donde el campo nombre sea 'Llamada'. Utilizamos first() para obtener el primer resultado o None si no hay coincidencias.
        llamadas_gestion = Tipo_gestion.objects.filter(
            nombre='Llamada').first()

        # Filtramos el modelo Gestiones para contar todas las gestiones asociadas al aspirante actual (obj) y que tengan el tipo de gestión encontrado (llamadas_gestion). count() devuelve el número de estas gestiones.
        if llamadas_gestion:
            cantidad_llamadas = Gestiones.objects.filter(
                cel_aspirante=obj,
                tipo_gestion=llamadas_gestion
            ).count()

            # Si se encontró un tipo de gestión, devolvemos el conteo de las gestiones de tipo 'Llamada'.
            return cantidad_llamadas
        return 0



    # Funcion para llevar el conteo de mensajes de texto
    def get_cantidad_mensajes_texto(self, obj):
        # Se busca el primer objeto en Tipo_gestion donde el campo nombre sea 'SMS'. Utilizamos first() para obtener el primer resultado o None si no hay coincidencias.
        mensajes_texto_gestion = Tipo_gestion.objects.filter(
            nombre='SMS').first()

        # Filtramos el modelo Gestiones para contar todas las gestiones asociadas al aspirante actual (obj) y que tengan el tipo de gestión encontrado (llamadas_gestion). count() devuelve el número de estas gestiones.
        if mensajes_texto_gestion:
            cantidad_mensajes_texto = Gestiones.objects.filter(
                cel_aspirante=obj,
                tipo_gestion=mensajes_texto_gestion
            ).count()

            # Si se encontró un tipo de gestión, devolvemos el conteo de las gestiones de tipo 'SMS'.
            return cantidad_mensajes_texto
        return 0



    # Funcion para llevar el conteo de gestiones por whatsap
    def get_cantidad_whatsapp(self, obj):
        # Se busca el primer objeto en Tipo_gestion donde el campo nombre sea 'Whatpsap'. Utilizamos first() para obtener el primer resultado o None si no hay coincidencias.
        whatsapp_gestion = Tipo_gestion.objects.filter(
            nombre='Whatpsap').first()

        # Filtramos el modelo Gestiones para contar todas las gestiones asociadas al aspirante actual (obj) y que tengan el tipo de gestión encontrado (llamadas_gestion). count() devuelve el número de estas gestiones.
        if whatsapp_gestion:
            cantidad_whatsapp = Gestiones.objects.filter(
                cel_aspirante=obj,
                tipo_gestion=whatsapp_gestion
            ).count()

            # Si se encontró un tipo de gestión, devolvemos el conteo de las gestiones de tipo 'SMS'.
            return cantidad_whatsapp
        return 0



    # Funcion para llevar el conteo  de gestiones
    def get_cantidad_gestiones(self, obj):
        cantidad_gestiones = Gestiones.objects.filter(
            cel_aspirante=obj).count()
        return cantidad_gestiones
    
    
    # Función para obtener la fecha de la última gestión del celular adicional
    def get_fecha_ultima_gestion(self, obj):
        ultima_gestion = Gestiones.objects.filter(
            cel_aspirante=obj,
            fecha__isnull=False
        ).order_by('-fecha').first()
        if ultima_gestion:
            return ultima_gestion.fecha
        return None
   

class TipoGestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tipo_gestion
        fields = '__all__'


class AsesorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asesores
        fields = '__all__'


class GestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gestiones
        fields = '__all__'


class ProgramaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Programa
        fields = '__all__'


class EmpresaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Empresa
        fields = '__all__'
        
        
class ProcesoSerializer(serializers.ModelSerializer):
    
    class  Meta:
        model = Proceso
        fields = '__all__'
    

class TipificacionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Tipificacion
        fields = '__all__'