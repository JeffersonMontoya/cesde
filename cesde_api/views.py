from .filters import *
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
import pandas as pd
from .models import *
from .serializer import *
from .serializer_filters import *
from .serializer_historico import *
from .serializer_aspirante import *
from io import StringIO
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import NotFound
from .estadisticas import *
from rest_framework.decorators import action
from django.shortcuts import redirect

import logging

# Configurar el logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class SedeViewSet(viewsets.ModelViewSet):
    queryset = Sede.objects.all()
    serializer_class = SedeSerializer
    filter_backends = (DjangoFilterBackend,)

class EstadoViewSet(viewsets.ModelViewSet):
    queryset = Estados.objects.all()
    serializer_class = EstadoSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = EstadosFilter


class AspiranteViewSet(viewsets.ModelViewSet):
    queryset = Aspirantes.objects.all()
    serializer_class = AspiranteSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProcesosFilter  # Especifica la clase de filtro aquí

    
    def list(self, request, *args, **kwargs):
        # Filtrar el queryset según los parámetros del request
        filtered_queryset = self.filter_queryset(self.get_queryset())

        # Serializar los aspirantes filtrados
        serializer = self.get_serializer(filtered_queryset, many=True)
        aspirantes = serializer.data

        # Obtener estadísticas generales para el queryset filtrado
        estadisticas_generales = obtener_estadisticas_generales(filtered_queryset)

        # Crear la respuesta personalizada
        response_data = {
            'aspirantes': aspirantes,
            'estadisticas': estadisticas_generales,
        }

        return Response(response_data)

    # Action for Process 1
    @action(detail=False, methods=['get'], url_path='proceso-1')
    def proceso_1(self, request):
        queryset = self.get_queryset().filter(proceso_id=1)
        serializer = self.get_serializer(queryset, many=True)

        estadisticas_generales = obtener_estadisticas_generales(queryset)
        return Response({
            'aspirantes': serializer.data,
            'estadisticas': estadisticas_generales,
        })

    # Action for Process 2
    @action(detail=False, methods=['get'], url_path='proceso-2')
    def proceso_2(self, request):
        queryset = self.get_queryset().filter(proceso_id=2)
        serializer = self.get_serializer(queryset, many=True)

        estadisticas_generales = obtener_estadisticas_generales(queryset)
        return Response({
            'aspirantes': serializer.data,
            'estadisticas': estadisticas_generales,
        })

    # Action for Process 3
    @action(detail=False, methods=['get'], url_path='proceso-3')
    def proceso_3(self, request):
        queryset = self.get_queryset().filter(proceso_id=3)
        serializer = self.get_serializer(queryset, many=True)

        estadisticas_generales = obtener_estadisticas_generales(queryset)
        return Response({
            'aspirantes': serializer.data,
            'estadisticas': estadisticas_generales,
        })


# view para filters aspirantes
class AspiranteFilterViewSet(viewsets.ModelViewSet):
    queryset = Aspirantes.objects.all()  # Conjunto de datos a mostrar
    serializer_class = AspiranteFilterSerializer # Serializador para convertir datos a JSON
    filter_backends = (DjangoFilterBackend,) # Habilita el filtrado usando django-filter
    filterset_class = AspirantesFilter  # Especifica la clase de filtro


# class ProcesosFilterView(generics.ListAPIView):
#     queryset = Aspirantes.objects.all()
#     serializer_class = AspiranteFilterSerializer
#     filterset_class = ProcesosFilter


class TipoGestionViewSet(viewsets.ModelViewSet):
    queryset = Tipo_gestion.objects.all()
    serializer_class = TipoGestionSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = Tipo_gestionFilter


class AsesoresViewSet(viewsets.ModelViewSet):
    queryset = Asesores.objects.all()
    serializer_class = AsesorSerializer
    filter_backends = (DjangoFilterBackend)
    


class GestionViewSet(viewsets.ModelViewSet):
    queryset = Gestiones.objects.all()
    serializer_class = GestionSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = GestionesFilter
    
 
class AsesorViewSet(viewsets.ModelViewSet):
    queryset = Asesores.objects.all()
    serializer_class = AsesorSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AsesoresFilter


class ProgramaViewSet(viewsets.ModelViewSet):
    queryset = Programa.objects.all()
    serializer_class = ProgramaSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProgramaFilter


# Proporciona operaciones CRUD (crear, leer, actualizar, eliminar) para el modelo.
class EmpresaViewSet(viewsets.ModelViewSet):
    # Especifica datos que deben ser consultados y retornados a la vista
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = EmpresaFilter

class Cargarcsv(APIView):
    permission_classes = [AllowAny]  # Permitir acceso a cualquiera

    def post(self, request, format=None):
        try:
            predictivo_file = request.FILES.get('predictivo')
            matricula_file = request.FILES.get('matricula')
            whatsapp_file = request.FILES.get('whatsapp')
            sms_file = request.FILES.get('SMS')

            if not predictivo_file or not matricula_file:
                return Response({"error": "se requieren al menos los archivos predictivo y matricula"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # BD Matriculas
                data_set1 = matricula_file.read().decode('UTF-8')
                io_string1 = StringIO(data_set1)
                df1 = pd.read_csv(io_string1)
                df1['Celular'] = df1['Celular'].astype(str)

                # BD predictivo
                data_set2 = predictivo_file.read().decode('UTF-8')
                io_string2 = StringIO(data_set2)
                df2 = pd.read_csv(io_string2)
                df2['TEL1'] = df2['TEL1'].astype(str)
                df2['cel_modificado'] = df2['TEL1'].apply(lambda x: x[2:] if len(
                    x) == 12 else (x[1:] if len(x) == 11 else 'Número no válido'))

                # BD Whatsapp
                data_set3 = whatsapp_file.read().decode('UTF-8')
                io_string3 = StringIO(data_set3)
                df3 = pd.read_csv(io_string3, skiprows=7)
                df3['CUSTOMER_PHONE'] = df3['CUSTOMER_PHONE'].astype(str)
                df3['cel_modificado'] = df3['CUSTOMER_PHONE'].apply(
                    lambda x: x[2:] if len(x) == 12 else x)

                # BD SMS
                data_set4 = sms_file.read().decode('UTF-8')
                io_string4 = StringIO(data_set4)
                df4 = pd.read_csv(io_string4, skiprows=7)
                df4['TELEPHONE'] = df4['TELEPHONE'].astype(str)
                df4['cel_modificado'] = df4['TELEPHONE'].apply(
                    lambda x: x[1:] if len(x) == 11 else x)

                # Unir los DataFrames
                df_unido = pd.merge(df1, df2, left_on='Celular',
                                    right_on='cel_modificado', how='right')
                df_unido = pd.merge(
                    df_unido, df3, on='cel_modificado', how='left')
                df_unido = pd.merge(
                    df_unido, df4, on='cel_modificado', how='left')

                # Seleccionar las columnas específicas que deseas mostrar
                columnas_deseadas = ['cel_modificado',
                                    'DATE_x', 'CIUDAD', 'NOMBRE', 'Estado']
                df_result = df_unido[columnas_deseadas]

                df_unido.to_csv('BD_Unidas1', index=False)

                print(df_result)
                return Response(status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error procesando los archivos CSV: {e}")
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Error en la función: {e}")
            return Response({'error': 'Error interno del servidor'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    serializer_class = EmpresaSerializer


class ProcesoViewSet(viewsets.ModelViewSet):
    queryset = Proceso.objects.all()
    serializer_class = ProcesoSerializer


class TipificacionViewSet(viewsets.ModelViewSet):
    queryset = Tipificacion.objects.all()
    serializer_class = TipificacionSerializer
    

class AspiranteHistoricoView(viewsets.ModelViewSet):
    queryset = Aspirantes.objects.all()
    serializer_class = HistoricoSerializer

    
