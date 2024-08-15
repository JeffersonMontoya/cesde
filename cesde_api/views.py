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
from django.db.models import Sum, Count, Case, When
from .serializer_asesores import ConsultaAsesoresSerializer
from django.db.models.functions import Coalesce
from .estadisticas import *
from rest_framework.decorators import action
from django.db.models import Count, OuterRef, Subquery
from django.shortcuts import get_object_or_404

import logging
# Configurar el logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

from django_filters.rest_framework import DjangoFilterBackend
from .filters import *


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


# view para filters generales 
class AspiranteFilterViewSet(viewsets.ModelViewSet):
    queryset = Aspirantes.objects.all()  # Conjunto de datos a mostrar
    # Serializador para convertir datos a JSON
    serializer_class = AspiranteFilterSerializer
    filter_backends = (DjangoFilterBackend,)# Habilita el filtrado usando django-filter
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

    @action(detail=False, methods=['get'], url_path='proceso-empresa')
    def empresa(self, request):
        """
        Filtro aspirantes para el proceso con nombre 'Empresa' y aplica filtros generales.
        """
        proceso = get_object_or_404(Proceso, nombre="empresa")
        queryset = self.get_queryset().filter(proceso=proceso)
        
        # Aplica filtros generales
        filterset = AspirantesFilter(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs

        # Serializa los datos
        serializer = AspiranteFilterSerializer(queryset, many=True)
        
        return Response({
            'aspirantes': serializer.data,
        })

    @action(detail=False, methods=['get'], url_path='proceso-extensiones')
    def extensiones(self, request):
        """
        Filtro aspirantes para el proceso con nombre 'Extensiones' y aplica filtros generales.
        """
        proceso = get_object_or_404(Proceso, nombre="extenciones")
        queryset = self.get_queryset().filter(proceso=proceso)
        
        # Aplica filtros generales
        filterset = AspirantesFilter(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs

        # Serializa los datos
        serializer = AspiranteFilterSerializer(queryset, many=True)
        
        return Response({
            'aspirantes': serializer.data,
        })

    @action(detail=False, methods=['get'], url_path='proceso-tecnico')
    def tecnico(self, request):
        """
        Filtro aspirantes para el proceso con nombre 'Técnico' y aplica filtros generales.
        """
        proceso = get_object_or_404(Proceso, nombre="técnicos")
        proceso = get_object_or_404(Proceso, nombre="técnicos")
        queryset = self.get_queryset().filter(proceso=proceso)
        
        # Aplica filtros generales
        filterset = AspirantesFilter(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs

        # Serializa los datos
        serializer = AspiranteFilterSerializer(queryset, many=True)
        
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
        proceso_nombre = request.query_params.get('proceso_nombre')

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

        # Filtrar gestiones por fecha
        gestiones_queryset = Gestiones.objects.filter(fecha__range=[fecha_inicio, fecha_fin])

        # Aplicar filtro por nombre del proceso si está presente
        if proceso_nombre:
            gestiones_queryset = gestiones_queryset.filter(
                cel_aspirante__proceso__nombre=proceso_nombre
            )

        estadisticas_por_fechas = obtener_estadisticas_por_fechas(gestiones_queryset, fecha_inicio, fecha_fin)
        contactabilidad = obtener_contactabilidad(gestiones_queryset)

        return Response({
            'estadisticas_por_fechas': estadisticas_por_fechas,
            'contactabilidad': contactabilidad,
        })
    
    @action(detail=False, methods=['get'], url_path='proceso-1')
    def estadisticas_extenciones(self, request):
        queryset = self.get_queryset().filter(proceso__nombre='extenciones')
        estadisticas_generales = obtener_estadisticas_generales(queryset)
        return Response({'estadisticas_extenciones': estadisticas_generales})

    @action(detail=False, methods=['get'], url_path='proceso-2')
    def estadisticas_tecnicos(self, request):
        queryset = self.get_queryset().filter(proceso__nombre='técnicos')
        estadisticas_generales = obtener_estadisticas_generales(queryset)
        return Response({'estadisticas_tecnicos': estadisticas_generales})

    @action(detail=False, methods=['get'], url_path='proceso-3')
    def estadisticas_extensiones(self, request):
        queryset = self.get_queryset().filter(proceso__nombre='empresa')
        estadisticas_generales = obtener_estadisticas_generales(queryset)
        return Response({'estadisticas_extensiones': estadisticas_generales})


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

    #función para conectar los archivos csv 
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
                df1['cel_modificado'] = df1['Celular']

                # BD predictivo
                data_set2 = predictivo_file.read().decode('UTF-8')
                io_string2 = StringIO(data_set2)
                df2 = pd.read_csv(io_string2)
                df2['TEL1'] = df2['TEL1'].astype(str)
                df2['cel_modificado'] = df2['TEL1'].apply(lambda x: x[2:] if len(
                    x) == 12 else (x[1:] if len(x) == 11 else 'no válido'))

                # BD Whatsapp
                data_set3 = whatsapp_file.read().decode('UTF-8')
                io_string3 = StringIO(data_set3)
                df3 = pd.read_csv(io_string3)
                df3['CUSTOMER_PHONE'] = df3['CUSTOMER_PHONE'].astype(str)
                df3['cel_modificado'] = df3['CUSTOMER_PHONE'].apply(
                    lambda x: x[2:] if len(x) == 12 else x)

                # BD SMS
                data_set4 = sms_file.read().decode('UTF-8')
                io_string4 = StringIO(data_set4)
                df4 = pd.read_csv(io_string4)
                df4['TELEPHONE'] = df4['TELEPHONE'].astype(str)
                df4['cel_modificado'] = df4['TELEPHONE'].apply(lambda x: x[1:] if len(x) == 11 else x)
                
                # Unir los DataFrames
                df_unido = pd.merge(df1, df2, left_on='cel_modificado', right_on='cel_modificado', how='right')
                df_unido_whatsapp = pd.merge(df_unido, df3, on='cel_modificado', how='left')
                df_unido_llamadas = pd.merge(df_unido, df4, on='cel_modificado', how='left')
                
                columnas_deseadas=[
                    'cel_modificado',
                    'Identificacion',
                    'DESCRIPTION_COD_ACT',
                    'Estado',
                    'NOMBRE',
                    'CorreoElectronico',
                    'Programa',
                    'Sede',
                    'AGENT_ID',
                    'AGENT_NAME',
                    'DATE',
                    'COMMENTS',
                    'PROCESO',
                    'NitEmpresa'
                    ]
                
                columnas_deseadas_whatsapp = columnas_deseadas + ['CHANNEL']
                
                df_result_whatsapp = df_unido_whatsapp[columnas_deseadas_whatsapp]
                df_result_llamadas = df_unido_llamadas[columnas_deseadas]

                #funcion para validar los datos antes de ingresarlos a la BD                
                def validarDatos(row):
                    #validar Estado
                    validar_estado = ['DESCRIPTION_COD_ACT']
                    estado_descargo = [
                        'Sin_interes', 
                        'Otra_area_de_interes',
                        'Ya_esta_estudiando_en_otra_universidad',
                        'Sin_tiempo',
                        'Sin_perfil',
                        'Eliminar_de_la_base',
                        'Proxima_convocatoria',
                        'No_manifiesta_motivo',
                        'Por_ubicacion',
                        'Imposible_contacto',
                        'Numero_invalido',
                        'Se_remite_a_otras_áreas_'
                    ]
                    estado_en_gestion = [
                        'Volver_a_llamar',
                        'Primer_intento_de_contacto',
                        'Segundo_intento_de_contacto',
                        'Tercer_intento_de_contacto',
                        'Fuera_de_servicio',
                        'TIMEOUTACW',
                        'Interesado_en_seguimiento',
                        'En_proceso_de_selección',
                        'Cliente_en_seguimiento',
                        'Informacion_general_',
                        'Cuelga_Telefono',
                        'Liquidacion'
                    ]
                    estado_liquidado = [
                        'Matriculado',                        
                    ]
                    
                    if pd.isna(row['Estado']):
                        # Verificar si alguna de las columnas en validar_estado tiene un valor en estado_descargo
                        if any(row[col] in estado_descargo for col in validar_estado if col in row):
                            return 'Descartado'
                        # verifica si alguna de las columnas en validar_estado tiene valor en estado_en_gestion
                        if  any(row[col] in estado_en_gestion for col in validar_estado if col in row):
                            return 'En Gestión'
                        # verifica si alguna de las columnas en validar-estado tiene valor en estado_liquidado
                        if any(row[col] in estado_liquidado for col in validar_estado if col in row):
                            return 'liquidado'
                        # Verificar si alguna de las columnas en validar_estado está vacía
                        if any(pd.isna(row[col]) for col in validar_estado if col in row):
                            return 'Sin gestión'
                        else:
                            return 'En Gestión'
                        
                    else:
                        return row['Estado']
                    
                #llenando datos vacíos con valores predeterminados
                df_result_whatsapp.loc[:, 'Estado'] = df_unido_whatsapp.apply(lambda row: validarDatos(row), axis=1)
                df_result_llamadas.loc[:, 'Estado'] = df_unido_llamadas.apply(lambda row: validarDatos(row), axis=1)

                df_result_llamadas['DESCRIPTION_COD_ACT'].fillna('no', inplace=True)
                df_result_whatsapp['DESCRIPTION_COD_ACT'].fillna('no', inplace=True)
                
                df_result_llamadas['Identificacion'].fillna('sin nit', inplace=True)
                df_result_whatsapp['Identificacion'].fillna('sin nit', inplace=True)
                
                df_result_llamadas['CorreoElectronico'].fillna('sin correo', inplace=True)
                df_result_whatsapp['CorreoElectronico'].fillna('sin correo', inplace=True)
                
                df_result_llamadas['Programa'].fillna('sin programa', inplace=True)
                df_result_whatsapp['Programa'].fillna('sin programa', inplace=True)
                
                df_result_llamadas['Sede'].fillna('sin sede', inplace=True)
                df_result_whatsapp['Sede'].fillna('sin sede', inplace=True)
                
                df_result_whatsapp['AGENT_ID'].fillna(0, inplace=True)
                df_result_llamadas['AGENT_ID'].fillna(0, inplace=True)
                df_result_llamadas['AGENT_ID'] = df_result_llamadas['AGENT_ID'].astype(int)
                df_result_whatsapp['AGENT_ID'] = df_result_whatsapp['AGENT_ID'].astype(int)
                
                df_result_whatsapp['NitEmpresa'].fillna('sin empresa', inplace=True)
                df_result_llamadas['NitEmpresa'].fillna('sin empresa', inplace=True)
                
                
                df_result_llamadas.to_csv('llamadas', index=False)
                df_result_whatsapp.to_csv('whatsapp', index=False)
                
                self.llenarBD(df_result_llamadas)
                self.llenarBD(df_result_whatsapp)
                
                return Response("Los archivos se cargaron con éxito", status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error procesando los archivos CSV: {e}")
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Error en la función: {e}")
            return Response({'error': 'Error interno del servidor'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # función para agregar a la base de datos    
    def llenarBD(self,df):
                    for index, row in df.iterrows():
                        #modelo estado
                        if pd.notna(row['Estado']):
                            Estados.objects.update_or_create(
                                nombre=row['Estado']
                            ) 
                         
                        #modelo procesos
                        if pd.notna(row['PROCESO']):
                            Proceso.objects.update_or_create(
                                nombre=row['PROCESO']
                            )
                        
                        #modelo asesores
                        if pd.notna(row['AGENT_ID']):
                            Asesores.objects.update_or_create(
                                id = row['AGENT_ID'],
                                defaults={
                                    'nombre_completo' : row['AGENT_NAME'] 
                                }
                            )
                        
                        #modelo programa 
                        if pd.notna(row['Programa']):
                            Programa.objects.update_or_create(
                                nombre = row['Programa']
                            )
                        
                        #modelo sede
                        if pd.notna(row['Sede']):
                            Sede.objects.update_or_create(
                                nombre = row['Sede']
                            )
                        
                        #modelo empresa
                        if pd.notna(row['NitEmpresa']):
                            Empresa.objects.update_or_create(
                                nit = row['NitEmpresa']
                            )
                        
                        # validando si hubo contacto o no en base a las tipificaciones
                        contacto = [
                            'Otra_area_de_interés', 
                            'Ya_esta_estudiando_en_otra_universidad',
                            'Sin_interes',
                            'Sin_tiempo',
                            'Eliminar_de_la_base',
                            'Próxima_convocatorio',
                            'No_Manifiesta_motivo',
                            'Por_ubicación',
                            'Matriculado',
                            'Liquidacion',
                            'En_proceso_de_selección',
                            'Interesado_en_seguimiento',
                            'Volver_a_llamar'
                            ]
                        
                        no_contacto = [
                            'Primer_intento_de_contacto',
                            'Segundo_intento_de_contacto',
                            'Tercer_intento_de_contacto',
                            'Fuera_de_servicio',
                            'Imposible_contacto',
                            'Número_inválido',
                            'Sin_perfil'
                        ] 
                        def contactabilidad(row):
                            if row['DESCRIPTION_COD_ACT'] in no_contacto:
                                return False
                            elif row['DESCRIPTION_COD_ACT'] in contacto: 
                                return True
                            return False
                        #modelo tipificacion
                        tipificaciones = { 
                            'Matriculado': 1.0,
                            'Liquidacion': 2.0,
                            'Número_inválido': 3.0,
                            'Imposible_contacto': 4.0,
                            'Por_ubicacion': 5.0,
                            'No_Manifiesta_motivo':6.0,
                            'Proxima_convocatoria': 7.0,
                            'Eliminar_de_la_base': 8.0,
                            'Sin_perfil': 9.0,
                            'Sin_tiempo': 10.0,
                            'Sin_interes': 11.0,
                            'Ya_esta_estudiando_en_otra_universidad': 12.0,
                            'Otra_area_de_interés': 13.0,
                            'En_proceso_de_selección': 14.0,
                            'Interesado_en_seguimiento': 15.0,
                            'Volver_a_llamar': 16.0,
                            'Fuera_de_servicio': 17.0,
                            'Tercer_intento_de_contacto': 18.0,
                            'Segundo_intento_de_contacto': 19.0,
                            'Primer_intento_de_contacto': 20.0,
                            'Informacion_general_': 21.0,
                            'No_Manifiesta_motivo': 22.0,
                            'no': 23.0,
                            'Cliente_en_seguimiento': 24.0, 
                            'TIMEOUTCHAT':25.0,
                            'Equivocado': 26.0,
                            'Se_remite_a_otras_áreas': 27.0,
                            'Otra_area_de_interes':28.0,
                            'TIMEOUTACW': 29.0,
                            'Cuelga_Telefono': 30.0,
                            'nan':31.0,
                            '': 32.0,
                            '-': 33.0
                        }
                        if pd.isna(row['DESCRIPTION_COD_ACT']) or row['DESCRIPTION_COD_ACT'].strip() == '':
                            valor_tipificacion = 31.0  # Valor por defecto para 'nan' o cadenas vacías
                        else:
                            valor_tipificacion = tipificaciones.get(row['DESCRIPTION_COD_ACT'], 0.0)
                        Tipificacion.objects.update_or_create(
                            nombre = row['DESCRIPTION_COD_ACT'],
                            defaults={
                                'contacto' : contactabilidad(row),
                                'valor_tipificacion' : valor_tipificacion
                            }
                        )
                        #modelo tipo_gestión
                        lista_tipo_gestion = ['WhatsApp','Llamada']
                        for tipo in lista_tipo_gestion:
                            Tipo_gestion.objects.update_or_create(
                                nombre = tipo
                            ) 
                        
                        #validaciones para llenar el modelo Aspirantes
                        def llenar_correo(row):
                            if pd.isna(row['CorreoElectronico']):
                                return 'sin correo'
                            else: 
                                return row['CorreoElectronico']
                            
                        def llenar_documento(row):
                            if pd.isna(row['Identificacion']):
                                return 'sin ID' 
                            else:
                                return row['Identificacion']
                            
                            
                        #modelo aspirantes
                        documento = llenar_documento(row)
                        correo = llenar_correo(row)
                        sede = Sede.objects.get(nombre=row['Sede'])
                        programa = Programa.objects.get(nombre=row['Programa'])
                        empresa = Empresa.objects.get(nit=row['NitEmpresa'])
                        proceso = Proceso.objects.get(nombre=row['PROCESO'])
                        estado = Estados.objects.get(nombre=row['Estado'])
                        
                        Aspirantes.objects.update_or_create(
                            celular=row['cel_modificado'],  # Campo único para buscar o crear
                            defaults={
                                'nombre': row['NOMBRE'],
                                'documento': documento,
                                'correo': correo,
                                'sede': sede,
                                'programa': programa,
                                'empresa': empresa,
                                'proceso': proceso,
                                'estado': estado
                            }
                        )

                        
                        def validar_tipo_gestion(row, df):
                            # Verificar si la columna 'CHANNEL' existe en el DataFrame
                            if 'CHANNEL' in df.columns:
                                # Verificar si el valor de 'CHANNEL' no es NaN
                                if pd.notna(row['CHANNEL']) and isinstance(row['CHANNEL'], str) and row['CHANNEL'] == 'whatsapp':
                                    return Tipo_gestion.objects.get(nombre='WhatsApp')
                            # Si la columna no existe o el valor es NaN, retornar 'llamadas'
                            return Tipo_gestion.objects.get(nombre='Llamada')
                        
                        def convertir_fecha(fecha_str):
                            try:
                                # Convertir la fecha de "MM/DD/YYYY HH:MM" a "YYYY-MM-DD HH:MM[:ss[.uuuuuu]]"
                                fecha_convertida = datetime.strptime(fecha_str, "%m/%d/%Y %H:%M")
                                return fecha_convertida
                            except ValueError as e:
                                print(f"Error al convertir la fecha: {e}")
                                return None
                        
                        def llenar_observaciones(row):
                            if pd.isna(row['COMMENTS']):
                                 return 'sin observaciones'
                            else:
                                return row['COMMENTS']
                        #modelo gestiones
                        try:
                            aspirante = Aspirantes.objects.get(celular=row['cel_modificado'])
                            tipificacion = Tipificacion.objects.get(nombre=row['DESCRIPTION_COD_ACT'])
                            asesor = Asesores.objects.get(id=row['AGENT_ID'])

                            tipo_gestion = validar_tipo_gestion(row, df)
                            fecha_convertida = convertir_fecha(row['DATE'])
                            observaciones = llenar_observaciones(row)
    
                            Gestiones.objects.update_or_create(
                                cel_aspirante = aspirante,
                                fecha = fecha_convertida,
                                tipo_gestion = tipo_gestion,
                                observaciones = observaciones , 
                                tipificacion = tipificacion,
                                asesor = asesor,
                            )
                        except Aspirantes.DoesNotExist:
                            print(f"Aspirante con celular {row['cel_modificado']} no encontrado.")
                        except Tipificacion.DoesNotExist:
                            print(f"Tipificación con código {row['DESCRIPTION_COD_ACT']} no encontrada.")
                        except Asesores.DoesNotExist:
                            print(f"Asesor con ID {row['AGENT_ID']} no encontrado.")
                        except Exception as e:
                            print(f"Error procesando la fila: {e}")
        
class ProcesoViewSet(viewsets.ModelViewSet):
    queryset = Proceso.objects.all()
    serializer_class = ProcesoSerializer


class TipificacionViewSet(viewsets.ModelViewSet, APIView):
    queryset = Tipificacion.objects.all()
    serializer_class = TipificacionSerializer
    
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
            gestiones = self.queryset.filter(cel_aspirante_id=celular_aspirante).order_by('-fecha')
            serializer = self.get_serializer(gestiones, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "Número de celular no proporcionado"}, status=400)
        
class ConsultaAsesoresViewSet(viewsets.ModelViewSet):
    queryset = Asesores.objects.all()
    serializer_class = ConsultaAsesoresSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AsesoresFilter

    def get_queryset(self):
        queryset = Asesores.objects.annotate(
            cantidad_llamadas=Coalesce(Sum(Case(When(gestiones__tipo_gestion__nombre='Llamada', then=1),
                output_field=models.IntegerField())), 0),

            cantidad_mensajes_texto=Coalesce(Sum(Case(When(gestiones__tipo_gestion__nombre='Mensaje de texto', then=1),
                output_field=models.IntegerField() )), 0),

            cantidad_whatsapp=Coalesce(Sum(Case(When(gestiones__tipo_gestion__nombre='WhatsApp', then=1),
                output_field=models.IntegerField())), 0),

            cantidad_gestiones=Count('gestiones', distinct=True),

        )

        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        id_asesor = self.request.query_params.get('id')

        if fecha_inicio:
            queryset = queryset.filter(gestiones__fecha__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(gestiones__fecha__lte=fecha_fin)
        if id_asesor:
            queryset = queryset.filter(id=id_asesor)

        return queryset.distinct()
    
