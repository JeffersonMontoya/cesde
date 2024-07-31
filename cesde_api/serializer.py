from .models import Aspirantes, Gestiones, Tipo_gestion, Estados
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
    class Meta:
        model = Aspirantes
        fields = '__all__'


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


