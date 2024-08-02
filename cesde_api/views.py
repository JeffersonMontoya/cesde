from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
import pandas as pd
from .models import *
from .serializer import *
from .serializer_filters import AspiranteFilterSerializer
from io import StringIO
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .filters import *


class DepartamentoViewSet(viewsets.ModelViewSet):
    queryset = Departamento.objects.all()
    serializer_class = DepartamentoSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = DepartamentosFilter # Especifica la clase de filtro


class CiudadViewSet(viewsets.ModelViewSet):
    queryset = Ciudad.objects.all()
    serializer_class = CiudadSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CiudadesFilter


class EstadoViewSet(viewsets.ModelViewSet):
    queryset = Estados.objects.all()
    serializer_class = EstadoSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = EstadosFilter


class AspiranteViewSet(viewsets.ModelViewSet):
    queryset = Aspirantes.objects.all() # Conjunto de datos a mostrar
    serializer_class = AspiranteSerializer # Serializador para convertir datos a JSON
    filter_backends = (DjangoFilterBackend,) # Habilita el filtrado usando django-filter
    filterset_class = AspirantesFilter # Especifica la clase de filtro

# view para filters aspirantes
class AspiranteFilterViewSet(viewsets.ModelViewSet):
    queryset = Aspirantes.objects.all() # Conjunto de datos a mostrar
    serializer_class = AspiranteFilterSerializer  # Serializador para convertir datos a JSON
    filter_backends = (DjangoFilterBackend,) # Habilita el filtrado usando django-filter
    filterset_class = AspirantesFilter # Especifica la clase de filtro


class TipoGestionViewSet(viewsets.ModelViewSet):
    queryset = Tipo_gestion.objects.all()
    serializer_class = TipoGestionSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = Tipo_gestionFilter


class AsesorViewSet(viewsets.ModelViewSet):
    queryset = Asesores.objects.all()
    serializer_class = AsesorSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AsesoresFilter


class GestionViewSet(viewsets.ModelViewSet):
    queryset = Gestiones.objects.all()
    serializer_class = GestionSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = GestionesFilter


class ProgramaViewSet(viewsets.ModelViewSet):
    queryset = Programa.objects.all()
    serializer_class = ProgramaSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProgramaFilter


class EmpresaViewSet(viewsets.ModelViewSet): # Proporciona operaciones CRUD (crear, leer, actualizar, eliminar) para el modelo.
    queryset =  Empresa.objects.all() # Especifica datos que deben ser consultados y retornados a la vista
    serializer_class = EmpresaSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = EmpresaFilter


class Cargarcsv(APIView):
    permission_classes = [AllowAny]  # Permitir acceso a cualquiera

    def post(self, request, format=None):
        archivos = request.FILES.getlist('archivos')
        for archivo in archivos: 
            data_set = archivo.read().decode('UTF-8')
            io_string = StringIO(data_set)
            df = pd.read_csv(io_string)
            print(df)

        return Response(status=status.HTTP_201_CREATED)

class EmpresaViewSet(viewsets.ModelViewSet):
    queryset =  Empresa.objects.all()
    serializer_class = EmpresaSerializer