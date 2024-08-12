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
from .estadisticas import *
from rest_framework.decorators import action
from django.db.models import Count, OuterRef, Subquery



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


# view para filters generales 
class AspiranteFilterViewSet(viewsets.ModelViewSet):
    queryset = Aspirantes.objects.all()  # Conjunto de datos a mostrar
    serializer_class = AspiranteFilterSerializer # Serializador para convertir datos a JSON
    filter_backends = (DjangoFilterBackend,) # Habilita el filtrado usando django-filter
    filterset_class = AspirantesFilter  # Especifica la clase de filtro


#  View para filters por procesos y por generales 
class FilterProcesosViewSet(viewsets.ViewSet):
    """
    Vista para mostrar aspirantes con filtros por procesos y filtros generales.
    """

    def get_queryset(self):
        """
        Devuelve el queryset para aspirantes.
        """
        return Aspirantes.objects.all()

    def list(self, request):
        """
        Devuelve la lista de aspirantes con filtros aplicados.
        """
        queryset = self.get_queryset()

        # Inicializa el filtro de procesos
        procesos_filter = ProcesosFilter(request.GET, queryset=queryset)
        if procesos_filter.is_valid():
            queryset = procesos_filter.qs
        
        # Aplica filtros generales
        filterset = AspirantesFilter(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs

        # Serializa los datos
        serializer = AspiranteFilterSerializer(queryset, many=True)
        

        return Response({
            'aspirantes': serializer.data,
        })

    @action(detail=False, methods=['get'], url_path='proceso-1')
    def empresa(self, request):
        """
        Filtro aspirantes para el proceso 1 y aplica filtros generales.
        """
        queryset = self.get_queryset().filter(proceso_id=1)
        
        # Aplica filtros generales
        filterset = AspirantesFilter(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs

        # Serializa los datos
        serializer = AspiranteFilterSerializer(queryset, many=True)
        
        # Obtiene estadísticas generales

        return Response({
            'aspirantes': serializer.data,
        })

    @action(detail=False, methods=['get'], url_path='proceso-2')
    def extensiones(self, request):
        """
        Filtro aspirantes para el proceso 2 y aplica filtros generales.
        """
        queryset = self.get_queryset().filter(proceso_id=2)
        
        # Aplica filtros generales
        filterset = AspirantesFilter(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs

        # Serializa los datos
        serializer = AspiranteFilterSerializer(queryset, many=True)
        
        # Obtiene estadísticas generales

        return Response({
            'aspirantes': serializer.data,
        })

    @action(detail=False, methods=['get'], url_path='proceso-3')
    def tecnico(self, request):
        """
        Filtro aspirantes para el proceso 3 y aplica filtros generales.
        """
        queryset = self.get_queryset().filter(proceso_id=3)
        
        # Aplica filtros generales
        filterset = AspirantesFilter(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs

        # Serializa los datos
        serializer = AspiranteFilterSerializer(queryset, many=True)
        
        # Obtiene estadísticas generales

        return Response({
            'aspirantes': serializer.data,
        })

# Estadisticas genrales, por procesos y por fechas
class EstadisticasViewSet(viewsets.GenericViewSet):
    """
    Vista para mostrar estadisticas generales por fecha y por proceso.
    """
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProcesosFilter  # Especifica la clase de filtros aquí
    

    def get_queryset(self):
        """
        Método para obtener el queryset de aspirantes.
        """
        return Aspirantes.objects.all()

    def list(self, request):
        """
        Lista las estadísticas generales si no se especifica un tipo.
        """
        filtered_queryset = self.filter_queryset(self.get_queryset())
        estadisticas_generales = obtener_estadisticas_generales(filtered_queryset)
        return Response({'estadisticas_generales': estadisticas_generales})

    @action(detail=False, methods=['get'], url_path='fechas')
    def estadisticas_por_fechas(self, request):
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')

        if not fecha_inicio or not fecha_fin:
            return Response({
                'detail': 'Las fechas de inicio y fin son requeridas en el formato YYYY-MM-DD.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'detail': 'Formato de fecha inválido. Use el formato YYYY-MM-DD.'
            }, status=status.HTTP_400_BAD_REQUEST)

        gestiones_queryset = Gestiones.objects.filter(fecha__date__range=[fecha_inicio, fecha_fin])
        estadisticas_por_fechas = obtener_estadisticas_por_fechas(gestiones_queryset, fecha_inicio, fecha_fin)
        contactabilidad = obtener_contactabilidad(gestiones_queryset)

        return Response({
            'estadisticas_por_fechas': estadisticas_por_fechas,
            'contactabilidad': contactabilidad,
        })

    @action(detail=False, methods=['get'], url_path='proceso-1')
    def estadisticas_empresas(self, request):
        queryset = self.get_queryset().filter(proceso_id=1)
        estadisticas_generales = obtener_estadisticas_generales(queryset)
        return Response({'estadisticas_empresas': estadisticas_generales})

    @action(detail=False, methods=['get'], url_path='proceso-2')
    def estadisticas_extenciones(self, request):
        queryset = self.get_queryset().filter(proceso_id=2)
        estadisticas_generales = obtener_estadisticas_generales(queryset)
        return Response({'estadisticas_extensiones': estadisticas_generales})

    @action(detail=False, methods=['get'], url_path='proceso-3')
    def estadisticas_tecnicos(self, request):
        queryset = self.get_queryset().filter(proceso_id=3)
        estadisticas_generales = obtener_estadisticas_generales(queryset)
        return Response({'estadisticas_tecnicos': estadisticas_generales})




class TipoGestionViewSet(viewsets.ModelViewSet):
    queryset = Tipo_gestion.objects.all()
    serializer_class = TipoGestionSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = Tipo_gestionFilter


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

