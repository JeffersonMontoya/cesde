from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
import pandas as pd
from .models import *
from .serializer import *
from io import StringIO
from rest_framework.permissions import AllowAny

import logging

# Configurar el logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

from django_filters.rest_framework import DjangoFilterBackend
# from .filters import AspirantesFilter, CiudadesFilter, DepartamentosFilter
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
        try:
            archivos = request.FILES.getlist('archivos')

            if len(archivos) < 4:
                return Response({'error': 'Se requieren 4 archivos CSV'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # BD Matriculas
                data_set1 = archivos[3].read().decode('UTF-8')
                io_string1 = StringIO(data_set1)
                df1 = pd.read_csv(io_string1)
                df1['Celular'] = df1['Celular'].astype(str)

                # BD predictivo
                data_set2 = archivos[2].read().decode('UTF-8')
                io_string2 = StringIO(data_set2)
                df2 = pd.read_csv(io_string2)
                df2['TEL1'] = df2['TEL1'].astype(str)
                df2['cel_modificado'] = df2['TEL1'].apply(lambda x: x[2:] if len(x) == 12 else (x[1:] if len(x) == 11 else 'Número no válido'))

                # BD Whatsapp
                data_set3 = archivos[1].read().decode('UTF-8')
                io_string3 = StringIO(data_set3)
                df3 = pd.read_csv(io_string3, skiprows=7)
                df3['CUSTOMER_PHONE'] = df3['CUSTOMER_PHONE'].astype(str)
                df3['cel_modificado'] = df3['CUSTOMER_PHONE'].apply(lambda x: x[2:] if len(x) == 12 else x)

                # BD SMS
                data_set4 = archivos[0].read().decode('UTF-8')
                io_string4 = StringIO(data_set4)
                df4 = pd.read_csv(io_string4, skiprows=7)
                df4['TELEPHONE'] = df4['TELEPHONE'].astype(str)
                df4['cel_modificado'] = df4['TELEPHONE'].apply(lambda x: x[1:] if len(x) == 11 else x)

                # Unir los DataFrames
                df_unido = pd.merge(df1, df2, left_on='Celular', right_on='cel_modificado', how='right')
                df_unido = pd.merge(df_unido, df3, on='cel_modificado', how='left')
                df_unido = pd.merge(df_unido, df4, on='cel_modificado', how='left')

                # Seleccionar las columnas específicas que deseas mostrar
                columnas_deseadas = ['cel_modificado','DATE_x','CIUDAD', 'NOMBRE', 'Estado']
                df_result = df_unido[columnas_deseadas]
                
                # df_result.to_csv('BD_Unidas2', index=False)

                print(df_result)
                return Response(status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error procesando los archivos CSV: {e}")
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Error en la función: {e}")
            return Response({'error': 'Error interno del servidor'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EmpresaViewSet(viewsets.ModelViewSet):
    queryset =  Empresa.objects.all()
    serializer_class = EmpresaSerializer
    
    
    

