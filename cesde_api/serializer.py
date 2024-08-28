from rest_framework import serializers
from .models import *
from datetime import datetime
from .models import *
from django.contrib.auth.models import User


class SedeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sede
        fields = '__all__'


class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estados
        fields = ['nombre']


class TipoGestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tipo_gestion
        fields = '__all__'


class GestionSerializer(serializers.ModelSerializer):
    tipo_gestion = serializers.SerializerMethodField()
    tipificacion = serializers.SerializerMethodField()
    asesor = serializers.SerializerMethodField()
    estado_aspirante = serializers.CharField(source='cel_aspirante.estado.nombre')

    class Meta:
        model = Gestiones
        fields = ['cel_aspirante', 'fecha', 'tipo_gestion',
                'observaciones', 'tipificacion', 'asesor', 'estado_aspirante']

    def get_tipo_gestion(self, obj):
        return obj.tipo_gestion.nombre

    def get_tipificacion(self, obj):
        return obj.tipificacion.nombre

    def get_asesor(self, obj):
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


import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def validate_username(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("El nombre de usuario debe tener al menos 5 caracteres.")
        if len(value) > 30:
            raise serializers.ValidationError("El nombre de usuario no puede tener más de 30 caracteres.")
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError("El nombre de usuario solo puede contener letras, números y guiones bajos.")
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("El nombre de usuario ya está en uso.")
        return value

    def validate_email(self, value):
        try:
            validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError("El formato del correo electrónico no es válido.")
        
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("El correo electrónico ya está registrado.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not re.search(r"[A-Za-z]", value):
            raise serializers.ValidationError("La contraseña debe contener al menos una letra.")
        if not re.search(r"[0-9]", value):
            raise serializers.ValidationError("La contraseña debe contener al menos un número.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise serializers.ValidationError("La contraseña debe contener al menos un carácter especial.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user