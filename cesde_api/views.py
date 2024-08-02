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


class DepartamentoViewSet(viewsets.ModelViewSet):
    queryset = Departamento.objects.all()
    serializer_class = DepartamentoSerializer

class CiudadViewSet(viewsets.ModelViewSet):
    queryset = Ciudad.objects.all()
    serializer_class = CiudadSerializer

class EstadoViewSet(viewsets.ModelViewSet):
    queryset = Estados.objects.all()
    serializer_class = EstadoSerializer

class AspiranteViewSet(viewsets.ModelViewSet):
    queryset = Aspirantes.objects.all()
    serializer_class = AspiranteSerializer

class TipoGestionViewSet(viewsets.ModelViewSet):
    queryset = Tipo_gestion.objects.all()
    serializer_class = TipoGestionSerializer

class AsesorViewSet(viewsets.ModelViewSet):
    queryset = Asesores.objects.all()
    serializer_class = AsesorSerializer

class GestionViewSet(viewsets.ModelViewSet):
    queryset = Gestiones.objects.all()
    serializer_class = GestionSerializer


class ProgramaViewSet(viewsets.ModelViewSet):
    queryset = Programa.objects.all()
    serializer_class = ProgramaSerializer


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
                df3 = pd.read_csv(io_string3, skiprows=7)
                df3['CUSTOMER_PHONE'] = df3['CUSTOMER_PHONE'].astype(str)
                df3['cel_modificado'] = df3['CUSTOMER_PHONE'].apply(lambda x: x[2:] if len(x) == 12 else x)

                # BD SMS
                data_set4 = sms_file.read().decode('UTF-8')
                io_string4 = StringIO(data_set4)
                df4 = pd.read_csv(io_string4, skiprows=7)
                df4['TELEPHONE'] = df4['TELEPHONE'].astype(str)
                df4['cel_modificado'] = df4['TELEPHONE'].apply(lambda x: x[1:] if len(x) == 11 else x)

                # Unir los DataFrames
                df_unido = pd.merge(df1, df2, left_on='cel_modificado', right_on='cel_modificado', how='right')
                df_unido = pd.merge(df_unido, df3, on='cel_modificado', how='left')
                df_unido = pd.merge(df_unido, df4, on='cel_modificado', how='left')

                # Seleccionar las columnas específicas que deseas mostrar
                columnas_deseadas = ["cel_modificado",
                                     "NOMBRE",
                                     "APELLIDO",
                                     "Identificacion",
                                     "CorreoElectronico",
                                     "CIUDAD",
                                     "Estado",
                                    #  "PROCESO",
                                     "Programa",
                                     "NitEmpresa",
                                     "FECHAFINREG",
                                     "DATE_x",
                                     "DATE_y",
                                     "COMMENTS_x",
                                     "COMMENTS_y",
                                     
                                    ]
                df_result = df_unido[columnas_deseadas]
                
                # df_result.to_csv('BD_Unidas2', index=False)

                print(df_result)
                return Response("Los archivos se cargaron con éxito", status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error procesando los archivos CSV: {e}")
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Error en la función: {e}")
            return Response({'error': 'Error interno del servidor'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # def guardarDatos(self, df):
    #     for index, row in df.iterrows():
            

class EmpresaViewSet(viewsets.ModelViewSet):
    queryset =  Empresa.objects.all()
    serializer_class = EmpresaSerializer
    
