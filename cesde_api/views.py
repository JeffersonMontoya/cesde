from rest_framework.pagination import PageNumberPagination
from .filters import *
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, mixins, generics,filters
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from .serializer import *
from .serializer_filters import *
from .serializer_historico import *
from django.db.models import Subquery, OuterRef, Count
from .serializer_asesores import ConsultaAsesoresSerializer
from .estadisticas import *
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination


import logging
# Configurar el logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class CustomPagination(PageNumberPagination):
    """
    Clase de paginación personalizada para usar con DRF.
    """
    page_size = 10  # Número de registros por página
    page_size_query_param = 'page_size'
    max_page_size = 100  # Tamaño máximo de página permitido

    def get_paginated_response(self, data):
        """
        Devuelve una respuesta paginada que incluye la información de paginación.
        """
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.page.paginator.per_page,
            'results': data,
            'next': self.get_next_link(),
            'previous': self.get_previous_link()
        })


class SedeViewSet(viewsets.ModelViewSet):
    queryset = Sede.objects.all()
    serializer_class = SedeSerializer
    filter_backends = (DjangoFilterBackend,)
    pagination_class = None  # Desactiva la paginación


class EstadoViewSet(viewsets.ModelViewSet):
    queryset = Estados.objects.all()
    serializer_class = EstadoSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = EstadosFilter
    pagination_class = None  # Desactiva la paginación


# view para filters generales
class AspiranteFilterViewSet(viewsets.ModelViewSet):
    """
    Vista para mostrar aspirantes con filtrado y paginación.
    """
    queryset = Aspirantes.objects.all()  # Conjunto de datos a mostrar
    serializer_class = AspiranteFilterSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AspirantesFilter  # Especifica la clase de filtro
    pagination_class = CustomPagination  # Configura la paginación personalizada

    def list(self, request, *args, **kwargs):
        """
        Devuelve la lista de aspirantes con filtros aplicados.
        """
        # Inicializa el filtro de procesos
        procesos_filter = ProcesosFilter(request.GET, queryset=self.queryset)
        if procesos_filter.is_valid():
            queryset = procesos_filter.qs

        # Aplica filtros generales
        filterset = AspirantesFilter(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs

        # Aplica la paginación
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(paginated_queryset, many=True)

        return paginator.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'], url_path='buscar-por-celular')
    def retrieve_by_celular(self, request, *args, **kwargs):
        """
        Devuelve un aspirante específico por número de celular.
        """
        celular = request.query_params.get('celular', None)

        if not celular:
            return Response({'detail': 'El parámetro celular es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            aspirante = self.queryset.get(celular=celular)
            serializer = self.get_serializer(aspirante)
            return Response(serializer.data)
        except Aspirantes.DoesNotExist:
            return Response({'detail': 'Aspirante no encontrado.'}, status=status.HTTP_404_NOT_FOUND)


class FilterProcesosViewSet(viewsets.ViewSet):
    """
    Vista para mostrar aspirantes con filtros por procesos y filtros generales.
    """
    pagination_class = CustomPagination  # Define la clase de paginación

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

        # Pagina el queryset
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        # Serializa los datos
        serializer = AspiranteFilterSerializer(paginated_queryset, many=True)

        # Devuelve la respuesta paginada
        return paginator.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'], url_path='proceso-empresa')
    def empresa(self, request):
        """
        Filtro aspirantes para el proceso con nombre 'Empresa' y aplica filtros generales.
        """
        proceso = get_object_or_404(Proceso, nombre="Empresas")
        queryset = self.get_queryset().filter(proceso=proceso)
        mes = request.query_params.get('mes')
        
        # Si mes url es igual a mes, me botara el mes dentro del proceso
        if mes:
            mes_url = mes;
            if mes_url:
                queryset = queryset.filter(fecha_ingreso=mes_url)
            else:
                return Response({'detail': 'Mes inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        # Aplica filtros generales
        filterset = AspirantesFilter(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs

        # Pagina el queryset
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        # Serializa los datos
        serializer = AspiranteFilterSerializer(paginated_queryset, many=True)

        # Devuelve la respuesta paginada
        return paginator.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'], url_path='proceso-extensiones')
    def extensiones(self, request):
        """
        Filtro aspirantes para el proceso con nombre 'Extensiones' y aplica filtros generales.
        """
        proceso = get_object_or_404(Proceso, nombre="extenciones")
        queryset = self.get_queryset().filter(proceso=proceso)
        mes = request.query_params.get('mes')
        
        # Si mes url es igual a mes, me botara el mes dentro del proceso
        if mes:
            mes_url = mes;
            if mes_url:
                queryset = queryset.filter(fecha_ingreso=mes_url)
            else:
                return Response({'detail': 'Mes inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        # Aplica filtros generales
        filterset = AspirantesFilter(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs

        # Pagina el queryset
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        # Serializa los datos
        serializer = AspiranteFilterSerializer(paginated_queryset, many=True)

        # Devuelve la respuesta paginada
        return paginator.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'], url_path='proceso-tecnico')
    def tecnico(self, request):
        """
        Filtro aspirantes para el proceso con nombre 'Técnico' y aplica filtros generales.
        """
        proceso = get_object_or_404(Proceso, nombre="Técnicos")
        queryset = self.get_queryset().filter(proceso=proceso)
        mes = request.query_params.get('mes')
        
        # Si mes url es igual a mes, me botara el mes dentro del proceso
        if mes:
            mes_url = mes;
            if mes_url:
                queryset = queryset.filter(fecha_ingreso=mes_url)
            else:
                return Response({'detail': 'Mes inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        # Aplica filtros generales
        filterset = AspirantesFilter(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs

        # Pagina el queryset
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        # Serializa los datos
        serializer = AspiranteFilterSerializer(paginated_queryset, many=True)

        # Devuelve la respuesta paginada
        return paginator.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'], url_path='mes')
    def aspirantes_por_mes(self, request):
        #Variable para los meses
        mes = request.query_params.get('mes')

        # Filtrar el queryset por el mes
        queryset = self.get_queryset().filter(fecha_ingreso=mes)

        # Paginación del queryset
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        # Serializa los datos
        serializer = AspiranteFilterSerializer(paginated_queryset, many=True)

        # Devuelve la respuesta paginada
        return paginator.get_paginated_response({
            'aspirantes': serializer.data
        })


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
        estadisticas_generales = obtener_estadisticas_generales(
            filtered_queryset)
        return Response({'estadisticas_generales': estadisticas_generales})

    @action(detail=False, methods=['get'], url_path='fechas')
    def estadisticas_por_fechas(self, request):
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        proceso_nombre = request.query_params.get('proceso_nombre')

        # Verifica que las fechas de inicio y fin estén presentes en los parámetros de la URL
        if not fecha_inicio or not fecha_fin:
            return Response({
                'detail': 'Las fechas de inicio y fin son requeridas en el formato YYYY-MM-DD.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Convierte las fechas de cadena a objetos datetime
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
            
            # Si las fechas de inicio y fin son iguales, incluimos hasta el final del día
            if fecha_inicio == fecha_fin:
                fecha_fin = fecha_fin + timedelta(days=1) - timedelta(seconds=1)  # Incluir todo el día hasta las 23:59:59
            else:
                # Si son diferentes, sumamos un día para incluir el día completo de la fecha_fin
                fecha_fin = fecha_fin + timedelta(days=1)

        except ValueError:
            # Devuelve un error si el formato de la fecha es inválido
            return Response({
                'detail': 'Formato de fecha inválido. Use el formato YYYY-MM-DD.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Filtrar gestiones por el rango de fechas especificado
        gestiones_queryset = Gestiones.objects.filter(
            fecha__range=[fecha_inicio, fecha_fin])

        # Aplicar filtro por nombre del proceso si está presente
        if proceso_nombre:
            # Esto convierte solo la primera letra a mayúscula
            proceso_nombre = proceso_nombre.capitalize()
            gestiones_queryset = gestiones_queryset.filter(
                cel_aspirante__proceso__nombre=proceso_nombre
            )

        # Obtener las estadísticas para el rango de fechas filtrado
        estadisticas_por_fechas = obtener_estadisticas_por_fechas(gestiones_queryset, fecha_inicio, fecha_fin)

        # Obtener la contactabilidad para el rango de fechas filtrado
        contactabilidad = obtener_contactabilidad(gestiones_queryset)

        # Calcular el tiempo promedio de WhatsApp y llamadas en minutos para el rango de fechas
        promedio_tiempo_wpp = gestiones_queryset.filter(
            tipo_gestion__nombre='WhatsApp'
        ).aggregate(
            promedio_wpp=Avg(F('tiempo_gestion') / 60) # Promedio en minutos
        )['promedio_wpp'] or 0

        promedio_tiempo_llamada = gestiones_queryset.filter(
            tipo_gestion__nombre='Llamada'
        ).aggregate(
            promedio_llamada=Avg(F('tiempo_gestion') / 60) # Promedio en minutos
        )['promedio_llamada'] or 0

        # Obtener el total de procesos en selección
        total_procesos_seleccion = gestiones_queryset.filter(
            tipificacion__nombre='En_proceso_de_selección'
        ).count()

        return Response({
            'estadisticas_por_fechas': estadisticas_por_fechas,
            'contactabilidad': contactabilidad,
            'promedio_tiempo_whatsapp': round(promedio_tiempo_wpp, 2),
            'promedio_tiempo_llamada': round(promedio_tiempo_llamada, 2),
            'en_seleccion_total': total_procesos_seleccion
        })
        

    @action(detail=False, methods=['get'], url_path='proceso-extenciones')
    def estadisticas_extenciones(self, request):
        queryset = self.get_queryset().filter(proceso__nombre='Extenciones')
        mes = request.query_params.get('mes')
        
        # Si mes url es igual a mes, me botara el mes dentro del proceso
        if mes:
            mes_url = mes;
            if mes_url:
                queryset = queryset.filter(fecha_ingreso=mes_url)
            else:
                return Response({'detail': 'Mes inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        estadisticas_generales = obtener_estadisticas_generales(queryset)
        return Response({'estadisticas_extenciones': estadisticas_generales})

    @action(detail=False, methods=['get'], url_path='proceso-técnicos')
    def estadisticas_tecnicos(self, request):
        queryset = self.get_queryset().filter(proceso__nombre='Técnicos')
        mes = request.query_params.get('mes')
        
        # Si mes url es igual a mes, me botara el mes dentro del proceso
        if mes:
            mes_url = mes;
            if mes_url:
                queryset = queryset.filter(fecha_ingreso=mes_url)
            else:
                return Response({'detail': 'Mes inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        estadisticas_generales = obtener_estadisticas_generales(queryset)
        return Response({'estadisticas_tecnicos': estadisticas_generales})

    @action(detail=False, methods=['get'], url_path='proceso-empresa')
    def estadisticas_empresa(self, request):    
        queryset = self.get_queryset().filter(proceso__nombre='Empresas')
        mes = request.query_params.get('mes')
        
        # Si mes url es igual a mes, me botara el mes dentro del proceso
        if mes:
            mes_url = mes;
            if mes_url:
                queryset = queryset.filter(fecha_ingreso=mes_url)
            else:
                return Response({'detail': 'Mes inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        estadisticas_generales = obtener_estadisticas_generales(queryset)
        return Response({'estadisticas_empresa': estadisticas_generales})
    
    @action(detail=False, methods={'get'}, url_path='mes')
    def estadisticas_mes(self, request):
        mes = request.query_params.get('mes')
        queryset = self.get_queryset().filter(fecha_ingreso=mes)
        estadisticas_generales = obtener_estadisticas_generales(queryset)
        return Response({'estadisticas_mes': estadisticas_generales})


class TipoGestionViewSet(viewsets.ModelViewSet):
    queryset = Tipo_gestion.objects.all()
    serializer_class = TipoGestionSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = Tipo_gestionFilter
    pagination_class = None  # Desactiva la paginación


class GestionViewSet(viewsets.ModelViewSet):
    queryset = Gestiones.objects.all()
    serializer_class = GestionSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = GestionesFilter
    pagination_class = CustomPagination  # Usar la paginación personalizada


class ProgramaViewSet(viewsets.ModelViewSet):
    queryset = Programa.objects.all()
    serializer_class = ProgramaSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProgramaFilter
    pagination_class = CustomPagination  # Usar la paginación personalizada
    pagination_class = None  # Desactiva la paginación

# Proporciona operaciones CRUD (crear, leer, actualizar, eliminar) para el modelo.


class EmpresaViewSet(viewsets.ModelViewSet):
    # Especifica datos que deben ser consultados y retornados a la vista
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = EmpresaFilter
    pagination_class = None  # Desactiva la paginación


class ProcesoViewSet(viewsets.ModelViewSet):
    queryset = Proceso.objects.all()
    serializer_class = ProcesoSerializer
    pagination_class = None  # Desactiva la paginación para esta vista


class TipificacionViewSet(viewsets.ModelViewSet, APIView):
    queryset = Tipificacion.objects.all()
    serializer_class = TipificacionSerializer
    pagination_class = None  # Desactiva la paginación para esta vista

    def create(self, request, *args, **kwargs):
        # Extraer datos del cuerpo de la solicitud
        data = request.data

        # Crear o actualizar la instancia
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()


class HistoricoViewSet(viewsets.ModelViewSet):
    queryset = Gestiones.objects.all()
    serializer_class = HistoricoGestionesSerializer

    @action(detail=False, methods=['get'])
    def historico(self, request):
        celular_aspirante = request.query_params.get('celular_aspirante')
        if celular_aspirante:
            # Ordena las gestiones por fecha en orden descendente
            gestiones = self.queryset.filter(
                cel_aspirante_id=celular_aspirante).order_by('-fecha')
            serializer = self.get_serializer(gestiones, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "Número de celular no proporcionado"}, status=400)


class ConsultaAsesoresViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = ConsultaAsesoresSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = AsesoresFilter
    pagination_class = None

    def get_queryset(self):
        return self.get_filtered_queryset()

    def get_filtered_queryset(self):
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        id_asesor = self.request.query_params.get('id')

        gestiones_subquery = Gestiones.objects.filter(
            asesor=OuterRef('pk')
        )

        if fecha_inicio and fecha_fin:
            gestiones_subquery = gestiones_subquery.filter(
                fecha__range=[fecha_inicio, fecha_fin]
            )

        queryset = Asesores.objects.annotate(
            tiene_gestiones=Subquery(gestiones_subquery.values('id')[:1])
        ).filter(tiene_gestiones__isnull=False)

        if id_asesor:
            queryset = queryset.filter(id=id_asesor)

        return queryset

    def list(self, request, *args, **kwargs):
        # Obtén el queryset filtrado
        queryset = self.filter_queryset(self.get_queryset())
        
        # Verifica si hay paginación
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            asesores_count = queryset.count()  # Conteo de asesores en la página
            return self.get_paginated_response({
                'asesores_count': asesores_count,
                'results': serializer.data
            })

        # Serializa los datos y cuenta los asesores
        serializer = self.get_serializer(queryset, many=True)
        asesores_count = queryset.count()  # Conteo de asesores sin paginación

        # Retorna la respuesta con los asesores y el conteo
        return Response({
            'total_asesores': asesores_count,
            'results': serializer.data
        })