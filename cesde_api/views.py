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
    filterset_class = ProcesosFilter  # Especifica la clase de filtro aquí

    def list(self, request, *args, **kwargs):
        # Filtrar el queryset según los parámetros del request
        filtered_queryset = self.filter_queryset(self.get_queryset())

        # Serializar los aspirantes filtrados
        serializer = self.get_serializer(filtered_queryset, many=True)
        aspirantes = serializer.data

        # Obtener estadísticas generales para el queryset filtrado
        estadisticas_generales = obtener_estadisticas_generales(
            filtered_queryset)

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
    # Serializador para convertir datos a JSON
    serializer_class = AspiranteFilterSerializer
    # Habilita el filtrado usando django-filter
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AspirantesFilter  # Especifica la clase de filtro


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
                    
                df_result_whatsapp.loc[:, 'Estado'] = df_unido_whatsapp.apply(lambda row: validarDatos(row), axis=1)
                df_result_llamadas.loc[:, 'Estado'] = df_unido_llamadas.apply(lambda row: validarDatos(row), axis=1)

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
            Estados.objects.update_or_create(
                nombre=row['Estado']
            )
             
            #modelo procesos
            Proceso.objects.update_or_create(
                nombre=row['PROCESO']
            )
            
            #modelo asesores
            Asesores.objects.update_or_create(
                id = row['AGENT_ID'],
                nombre_completo = row['AGENT_NAME'] 
            )
            
            #modelo programa 
            Programa.objects.update_or_create(
                nombre = row['Programa']
            )
            
            #modelo sede
            Sede.objects.update_or_create(
                nombre = row['Sede']
            )
            
            #modelo empresa
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
                'Próxima_convocatoria',
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
                'Número_inválido'
            ] 
            def contactabilidad(row):
                if row['DESCRIPTION_COD_ACT'] in no_contacto:
                    return False
                elif row['DESCRIPTION_COD_ACT'] in contacto: 
                    return True
                return False
            #modelo tipificacion
            Tipificacion.objects.update_or_create(
                nombre = row['DESCRIPTION_COD_ACT'],
                contacto = contactabilidad(row)
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
            try:
                documento = llenar_documento(row)
                correo = llenar_correo(row)
                sede = Sede.objects.get(nombre=row['Sede'])
                estado = Estados.objects.get(nombre=row['Estado'])
                programa = Programa.objects.get(nombre=row['Programa'])
                empresa = Empresa.objects.get(nit=row['NitEmpresa'])
                proceso = Proceso.objects.get(nombre=row['PROCESO'])
                
                Aspirantes.objects.update_or_create(
                    celular=row['cel_modificado'],  # Campo único para buscar o crear
                    defaults={
                        'nombre': row['NOMBRE'],
                        'documento': documento,
                        'correo': correo,
                        'sede': sede,
                        'estado': estado,
                        'programa': programa,
                        'empresa': empresa,
                        'proceso': proceso,
                    }
                )
            except Exception as e:
                return f"error procesando la fila {e}"
            
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
        print('datos cargados con éxito')
        
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