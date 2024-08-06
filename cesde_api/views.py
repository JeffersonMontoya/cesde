from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
import pandas as pd
from .models import *
from .serializer import *
from .serializer_filters import *
from io import StringIO
from rest_framework.permissions import AllowAny

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
                df2['cel_modificado'] = df2['TEL1'].apply(lambda x: x[2:] if len(x) == 12 else (x[1:] if len(x) == 11 else 'Número no válido'))

                # BD Whatsapp
                data_set3 = whatsapp_file.read().decode('UTF-8')
                io_string3 = StringIO(data_set3)
                df3 = pd.read_csv(io_string3)
                df3['CUSTOMER_PHONE'] = df3['CUSTOMER_PHONE'].astype(str)
                df3['cel_modificado'] = df3['CUSTOMER_PHONE'].apply(lambda x: x[2:] if len(x) == 12 else x)

                # BD SMS
                data_set4 = sms_file.read().decode('UTF-8')
                io_string4 = StringIO(data_set4)
                df4 = pd.read_csv(io_string4)
                df4['TELEPHONE'] = df4['TELEPHONE'].astype(str)
                df4['cel_modificado'] = df4['TELEPHONE'].apply(lambda x: x[1:] if len(x) == 11 else x)

                # Unir los DataFrames
                df_unido = pd.merge(df1, df2, left_on='cel_modificado', right_on='cel_modificado', how='right')
                df_unido = pd.merge(df_unido, df3, on='cel_modificado', how='left')
                df_unido = pd.merge(df_unido, df4, on='cel_modificado', how='left')

                # datos para cada modelo
                modelo_estado = [
                    "Estado"
                ]
                
                modelo_sede = [
                    "Sede"
                ]
                
                modelo_empresa = [
                    "NitEmpresa"
                ]
                
                modelo_programa = [
                    "TipoPrograma",
                    "Programa"
                ]
                
                modelo_tipificaciones = [
                    "RESULTADOREG",
                    "DESCRIPTION_COD_ACT_x",
                    "DESCRIPTION_COD_ACT_y",
                ]                
                
                modelo_asesores = [
                    "AGENT_ID_x",
                    "AGENT_ID_y",
                    "AGENT_NAME_x",
                    "AGENT_NAME_y"
                ]
                
                modelo_aspirantes = [
                    "cel_modificado",
                    "NOMBRE",
                    "Identificacion",
                    "CorreoElectronico",
                    "CIUDAD",
                    "Estado",
                    # "PROCESO",
                    "Programa",
                    "NitEmpresa",
                    "DESCRIPTION_COD_ACT_x",
                    "DESCRIPTION_COD_ACT_y",

                ]
                
                modelo_gestiones = [
                    "cel_modificado",
                    "FECHAFINREG",
                    "DATE_x",
                    "DATE_y",
                    "COMMENTS_x",
                    "COMMENTS_y",
                    "AGENT_ID_x",
                    "AGENT_ID_y",
                    "AGENT_NAME_x",
                    "AGENT_NAME_y",
                    "RESULTADOREG",
                    "DESCRIPTION_COD_ACT_x",
                    "DESCRIPTION_COD_ACT_y",
                    "AGENT_ID_x",
                    "AGENT_ID_y",
                    # "asesor_predictivo"
                ]
                
                modelo_procesos = [
                    "nombre"
                ]
                
                df_result = df_unido[modelo_aspirantes]
                
                def llenarDatos(row):
                    #validar Estado
                    validar_estado = ['DESCRIPTION_COD_ACT_x', 'DESCRIPTION_COD_ACT_y']
                    estado_descargo = [
                        'Sin_interes', 
                        'Otra_area_de_interes',
                        'Ya_esta_estudiando_en_otra_universidad',
                        'Sin_tiempo',
                        'Sin_perfil',
                        'Eliminar_de_la_base',
                        'Proxima_convocatoria',
                        'No_manifiesta_motivo',
                        'Por_ubicacion ',
                        'Imposible_contacto',
                        'Numero_invalido'
                    ]
                    estado_en_gestion = [
                        'Volver_a_llamar',
                        'Primer_intento_de_contacto',
                        'Segundo_intento_de_contacto',
                        'Tercer_intento_de_contacto',
                        'Fuera_de_servicio'
                    ]
                    if pd.isna(row['Estado']):
                        # Verificar si alguna de las columnas en validar_estado tiene un valor en estado_descargo
                        if any(row[col] in estado_descargo for col in validar_estado if col in row):
                            return 'Descartado'
                        # verifica si alguna de las columnas en validar_estado tiene valor en estado_en_gestion
                        if  any(row[col] in estado_en_gestion for col in validar_estado if col in row):
                            return 'En Gestión'
                        # Verificar si alguna de las columnas en validar_estado está vacía
                        if any(pd.isna(row[col]) for col in validar_estado if col in row):
                            return 'Sin gestión'
                        else:
                            return 'En gestion'
                        
                    else:
                        return row['Estado']
                        
           
                df_result['Estado'] = df_result.apply(lambda row: llenarDatos(row), axis=1)
                

                df_result.to_csv("aspirantes", index=False)
                
                return Response("Los archivos se cargaron con éxito", status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error procesando los archivos CSV: {e}")
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Error en la función: {e}")
            return Response({'error': 'Error interno del servidor'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class EmpresaViewSet(viewsets.ModelViewSet):
    queryset =  Empresa.objects.all()
    serializer_class = EmpresaSerializer
    serializer_class = EmpresaSerializer
   
class ProcesoViewSet(viewsets.ModelViewSet):
    queryset = Proceso.objects.all()
    serializer_class = ProcesoSerializer 
   
class TipificacionViewSet(viewsets.ModelViewSet):
    queryset = Tipificacion.objects.all()
    serializer_class = TipificacionSerializer    
