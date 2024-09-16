from rest_framework import  status
from rest_framework.views import APIView
from rest_framework.response import Response
import pandas as pd
from .models import *
from io import StringIO
from rest_framework.permissions import AllowAny
import pytz
import logging
from datetime import datetime as datetime1
import datetime 
import numpy as np

# Configurar el logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class Cargarcsv(APIView):
    permission_classes = [AllowAny]  # Permitir acceso a cualquiera
    # gestiones_acumuladas = []
    
    def __init__(self):
        #estados del aspirante segun la tipificación
        self.estado_descargo = ['Sin_interes','Otra_area_de_interes','Ya_esta_estudiando_en_otra_universidad','Sin_tiempo','Sin_perfil','Eliminar_de_la_base','Proxima_convocatoria','No_Manifiesta_motivo','Por_ubicacion','Imposible_contacto','Numero_invalido','Se_remite_a_otras_áreas_'
        ]

        self.estado_en_gestion = ['Volver_a_llamar','Primer_intento_de_contacto','Segundo_intento_de_contacto','Tercer_intento_de_contacto','Fuera_de_servicio','TIMEOUTACW','Interesado_en_seguimiento','En_proceso_de_selección','Cliente_en_seguimiento','Informacion_general_','Cuelga_Telefono','Liquidacion'
        ]
        
        self.estado_liquidado = ['Matriculado',]
        
        #contactabilidad segun la tipificación 
        self.contacto = ['Otra_area_de_interés','Ya_esta_estudiando_en_otra_universidad','Sin_interes','Sin_tiempo','Eliminar_de_la_base','Próxima_convocatorio','No_Manifiesta_motivo','Por_ubicación','Matriculado','Liquidacion','En_proceso_de_selección','Interesado_en_seguimiento','Volver_a_llamar'
        ]
        
        self.no_contacto = ['Primer_intento_de_contacto','Segundo_intento_de_contacto','Tercer_intento_de_contacto','Fuera_de_servicio','Imposible_contacto','Número_inválido','Sin_perfil'
        ]
        
        self.tipificaciones = {'Matriculado': 1.0,'Liquidacion': 2.0,'Número_inválido': 3.0,'Imposible_contacto': 4.0,'Por_ubicacion': 5.0,'No_Manifiesta_motivo': 6.0,'Proxima_convocatoria': 7.0,'Eliminar_de_la_base': 8.0,'Sin_perfil': 9.0,'Sin_tiempo': 10.0,'Sin_interes': 11.0,'Ya_esta_estudiando_en_otra_universidad': 12.0,'Otra_area_de_interés': 13.0,'En_proceso_de_selección': 14.0,'Interesado_en_seguimiento': 15.0,'Volver_a_llamar': 16.0,'Fuera_de_servicio': 17.0,'Tercer_intento_de_contacto': 18.0,'Segundo_intento_de_contacto': 19.0,'Primer_intento_de_contacto': 20.0,'Informacion_general_': 21.0,'no': 23.0,'Cliente_en_seguimiento': 24.0,'TIMEOUTCHAT': 25.0,'Equivocado': 26.0,'Se_remite_a_otras_áreas': 27.0,'Otra_area_de_interes': 28.0,'TIMEOUTACW': 29.0,'Cuelga_Telefono': 30.0,'nan': 31.0,'': 32.0,'-': 33.0
        }
        
        self.en_seguimiento = ['Volver_a_llamar']
        
        self.no_contactado = ['Primer_intento_de_contacto', 'Segundo_intento_de_contacto', 'Tercero_intento_de_contacto', 'Fuera_de_servicio']
    
        self.interesado = ['Matriculado', 'Liquidado', 'En_proceso_de_selección', 'Interesado_en_seguimiento']
        
        self.descartado = ['Número_inválido', 'Imposible_contacto', 'Por_ubicacion', 'No_Manifiesta_motivo',  'Proxima_convocatoria',  'Eliminar_de_la_base', 'Sin_perfil', 'Sin_tiempo', 'Sin_interes', 'Ya_esta_estudiando_en_otra_universidad',  'Otra_area_de_interés']
    
    def contactabilidad(self, row):
        if row['DESCRIPTION_COD_ACT'] in self.no_contacto:
            return False
        elif row['DESCRIPTION_COD_ACT'] in self.contacto:
            return True
        return False
    
    #funcion para actualizar el estado del aspirante
    def actualizar_estados_aspirantes(self):
        # Obtener todos los aspirantes menos los matriculados y liquidados
        aspirantes = Aspirantes.objects.exclude(
            estado__nombre__in=['matriculado', 'liquidado', 'Descartado', "cancelado"])

        for aspirante in aspirantes:
            # Obtener la última gestión para este aspirante
            ultima_gestion = Gestiones.objects.filter(cel_aspirante=aspirante).order_by('-fecha').first()

            if ultima_gestion:
                tipificacion = ultima_gestion.tipificacion.nombre

                if tipificacion in self.estado_descargo:
                    nombre_nuevo_estado = 'Descartado'
                elif tipificacion in self.estado_en_gestion:
                    nombre_nuevo_estado = 'En Gestión'
                elif tipificacion in self.estado_liquidado:
                    nombre_nuevo_estado = 'liquidado'
                else:
                    nombre_nuevo_estado = 'En Gestión'

                try:
                    nuevo_estado = Estados.objects.get(
                        nombre=nombre_nuevo_estado)
                    if aspirante.estado != nuevo_estado:
                        aspirante.estado = nuevo_estado
                        aspirante.save()
                except Exception as e:
                    print(f"Error al procesar el estado para {aspirante.celular}: {e}")
            else:
                # Si no hay gestión, asignar estado 'Sin gestión'
                sin_gestion_estado = Estados.objects.get(nombre='Sin gestión')
                if aspirante.estado != sin_gestion_estado:
                    aspirante.estado = sin_gestion_estado
                    aspirante.save()

        print("Actualización de estados completada.")
        
    def convertir_a_segundos(self, tiempo):
        try:
            # Intentar analizar el tiempo en formato hh:mm:ss AM/PM
            dt = datetime1.strptime(tiempo, '%I:%M:%S %p')
        except ValueError:
            try:
                # Intentar analizar el tiempo en formato hh:mm:ss (24 horas)
                dt = datetime1.strptime(tiempo, '%H:%M:%S')
            except ValueError:
                raise ValueError(f"Formato de tiempo inválido: {tiempo}")
        # Convertir el tiempo a segundos
        tiempo_en_segundos = dt.hour * 3600 + dt.minute * 60 + dt.second
        tiempo_int = int(tiempo_en_segundos)
        return tiempo_int
        
    # función para conectar los archivos csv
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
                df1 = pd.read_csv(io_string1, delimiter=';')
                df1['Celular'] = df1['Celular'].astype(str)
                df1['cel_modificado'] = df1['Celular']

                # BD predictivo
                data_set2 = predictivo_file.read().decode('UTF-8')
                io_string2 = StringIO(data_set2)
                df2 = pd.read_csv(io_string2, delimiter=';')
                df2['TEL1'] = df2['TEL1'].dropna()
                df2['TEL1'] = df2['TEL1'].fillna(0)
                df2['TEL1'] = df2['TEL1'].astype(int)
                df2['TEL1'] = df2['TEL1'].astype(str)
                # Filtrar y ajustar los números de teléfono
                df2['cel_modificado'] = df2['TEL1'].apply(lambda x: x[-10:] if len(x) >= 10 else None)
                # Eliminar las filas donde 'cel_modificado' es None (es decir, donde el número original tenía menos de 10 dígitos)
                df2 = df2.dropna(subset=['cel_modificado'])

                # BD Whatsapp
                if whatsapp_file:
                    data_set3 = whatsapp_file.read().decode('UTF-8')
                    io_string3 = StringIO(data_set3)
                    df3 = pd.read_csv(io_string3, delimiter=';')
                    df3['CUSTOMER_PHONE'].replace('---', np.nan, inplace=True)
                    df3['CUSTOMER_PHONE'].replace('-', np.nan, inplace=True)
                    df3['CUSTOMER_PHONE'].dropna()
                    df3['CUSTOMER_PHONE'] = df3['CUSTOMER_PHONE'].fillna(0)
                    df3['CUSTOMER_PHONE'] = df3['CUSTOMER_PHONE'].astype(int)
                    df3['CUSTOMER_PHONE'] = df3['CUSTOMER_PHONE'].astype(str)
                    df3['cel_modificado'] = df3['CUSTOMER_PHONE'].apply(lambda x: x[-10:] if len(x) >= 10 else None)
                    df3 = df3.dropna(subset=['cel_modificado'])
                    df3['TIME_ON_AGENT'].fillna(value='0:00:00', inplace=True)
                    df3['segundos'] = df3['TIME_ON_AGENT'].apply(self.convertir_a_segundos).astype(int)
                    df3.loc[:, 'segundos'] = df3['segundos'].astype(int)

                # BD SMS
                if sms_file:
                    data_set4 = sms_file.read().decode('UTF-8')
                    io_string4 = StringIO(data_set4)
                    df4 = pd.read_csv(io_string4, delimiter=';')
                    df4['TELEPHONE'].replace('---', np.nan, inplace=True)
                    df4['TELEPHONE'].replace('-', np.nan, inplace=True)
                    df4['TELEPHONE'].dropna()
                    df4['TELEPHONE'] = df4['TELEPHONE'].fillna(0)
                    df4['TELEPHONE'] = df4['TELEPHONE'].astype(str)
                    df4['cel_modificado'] = df4['TELEPHONE'].apply(lambda x: x[-10:] if len(x) >= 10 else None)
                    df4 = df4.dropna(subset=['cel_modificado'])
                    df4['TIME'].fillna(value='0', inplace=True)
                    df4['segundos'] = df4['TIME']
                    df4.loc[:, 'segundos'] = df4['segundos'].astype(int)
                    

                # Unir los DataFrames
                df_unido = pd.merge(df1, df2, left_on='cel_modificado', right_on='cel_modificado', how='right')
                if whatsapp_file:
                    df_unido_whatsapp = pd.merge(df_unido, df3, on='cel_modificado', how='outer')
                if sms_file:
                    df_unido_llamadas = pd.merge(df_unido, df4, on='cel_modificado', how='outer')

                columnas_deseadas = ['cel_modificado','Identificacion','DESCRIPTION_COD_ACT','Estado','NOMBRE','CORREO','CIUDAD','AGENT_ID','AGENT_NAME','DATE','COMMENTS','PROCESO','Empresa a la que se postula','Programa académico', 'segundos']

                columnas_deseadas_whatsapp = columnas_deseadas + ['CHANNEL']

                if whatsapp_file:
                    df_result_whatsapp = df_unido_whatsapp[columnas_deseadas_whatsapp]
                if sms_file:
                    df_result_llamadas = df_unido_llamadas[columnas_deseadas]
                    
                #validar estado 
                # if whatsapp_file:
                #     df_result_whatsapp['Estado'] = df_result_whatsapp['Estado'].fillna(df_result_whatsapp['Prospecto'])
                # if sms_file:
                #     df_result_llamadas['Estado']= df_result_llamadas['Estado'].fillna(df_result_llamadas['Prospecto'])

                # funcion para validar los datos antes de ingresarlos a la BD
                
                def validarDatos(row):
                    # validar Estado
                    validar_estado = ['DESCRIPTION_COD_ACT']
                
                    if pd.isna(row['Estado']):
                        # Verificar si alguna de las columnas en validar_estado tiene un valor en estado_descargo
                        if any(row[col] in self.estado_descargo for col in validar_estado if col in row):
                            return 'Descartado'
                        # verifica si alguna de las columnas en validar_estado tiene valor en estado_en_gestion
                        if any(row[col] in self.estado_en_gestion for col in validar_estado if col in row):
                            return 'En Gestión'
                        # verifica si alguna de las columnas en validar-estado tiene valor en estado_liquidado
                        if any(row[col] in self.estado_liquidado for col in validar_estado if col in row):
                            return 'liquidado'
                        # Verificar si alguna de las columnas en validar_estado está vacía
                        if any(pd.isna(row[col]) for col in validar_estado if col in row):
                            return 'Sin gestión'
                        else:
                            return 'En Gestión'

                    else:
                        return row['Estado']

                # llenando datos vacíos con valores predeterminados
                if whatsapp_file:
                    df_result_whatsapp.loc[:, 'Estado'] = df_unido_whatsapp.apply(lambda row: validarDatos(row), axis=1)
                if sms_file:
                    df_result_llamadas.loc[:, 'Estado'] = df_unido_llamadas.apply(lambda row: validarDatos(row), axis=1)

                def llenar_valores_predeterminados(df, columnas):
                    for columna, valor in columnas.items():
                        df.loc[:, columna] = df[columna].fillna(valor)

                # Definir los valores predeterminados
                valores_predeterminados = {
                    'Estado': 'Sin Gestion',
                    'Identificacion': '',
                    'CORREO': 'sin correo',
                    'Programa académico': 'sin programa',
                    'CIUDAD': 'sin sede',
                    'Empresa a la que se postula': 'sin empresa',
                    'Identificacion': 'sin ID',
                    'COMMENTS': 'sin observaciones'
                }

                # Aplicar la función a ambos DataFrames
                if sms_file:
                    llenar_valores_predeterminados(df_result_llamadas, valores_predeterminados)
                    df_result_llamadas['AGENT_ID'] = df_result_llamadas['AGENT_ID'].fillna(0).astype(int)
                    df_result_llamadas.to_csv('llamadas', index=False)
                    self.llenarBD(df_result_llamadas)
                else:
                    print("no se trabajo con el archivo de llamadas.")
                if whatsapp_file:
                    llenar_valores_predeterminados(df_result_whatsapp, valores_predeterminados)
                    df_result_whatsapp['AGENT_ID'] = df_result_whatsapp['AGENT_ID'].fillna(0).astype(int)
                    df_result_whatsapp.replace('', np.nan, inplace=True)
                    df_result_whatsapp.dropna(subset=['AGENT_NAME', 'DATE'], inplace=True)
                    df_result_whatsapp.to_csv('whatsapp', index=False)
                    self.llenarBD(df_result_whatsapp)
                else:
                    print("no se trabajo con el archivo de whatsapp.")

                return Response("Los archivos se cargaron con éxito", status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error procesando los archivos CSV: {e}")
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Error en la función: {e}")
            return Response({'error': 'Error interno del servidor'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def actualizar_o_crear_modelo(self, Model, **kwargs):
        Model.objects.update_or_create(**kwargs)

    def convertir_fecha(self, fecha_str):
        if not fecha_str or pd.isna(fecha_str):
            return None  # Retorna None si la fecha está vacía o es NaN
        try:
            # Convertir la fecha de "M/D/YYYY H:M" a un objeto datetime
            fecha_convertida = datetime.datetime.strptime(fecha_str, "%d/%m/%Y %H:%M")
            # Asignar la zona horaria deseada (por ejemplo, 'UTC')
            zona_horaria = pytz.timezone("UTC")  # Cambiaz 'UTC' a tu zona horaria si es necesario
            # Hacer el datetime aware
            fecha_convertida = zona_horaria.localize(fecha_convertida)
            return fecha_convertida
        except ValueError as e:
            print(f"Error al convertir la fecha: {e}")
            return None
        
    def validar_tipo_gestion(self ,row, df):
            # Verificar si la columna 'CHANNEL' existe en el DataFrame
            if 'CHANNEL' in df.columns:
                # Verificar si el valor de 'CHANNEL' no es NaN
                if pd.notna(row['CHANNEL']) and isinstance(row['CHANNEL'], str) and row['CHANNEL'] == 'whatsapp':
                    return Tipo_gestion.objects.get(nombre='WhatsApp')
            # Si la columna no existe o el valor es NaN, retornar 'llamadas'
            return Tipo_gestion.objects.get(nombre='Llamada')
        
    # función para agregar a la base de datos
    def llenarBD(self, df):
        gestiones_a_guardar = []
        aspirantes_a_crear = []
        aspirantes_a_actualizar = []
        celulares_a_guardar = set()
        
        celulares_existentes = set(Aspirantes.objects.filter(
            celular__in=df['cel_modificado'].unique()
        ).values_list('celular', flat=True))

        # Modelo Tipo_gestion
        for tipo in ['WhatsApp', 'Llamada']:
            self.actualizar_o_crear_modelo(Tipo_gestion, nombre=tipo)
        
        for index, row in df.iterrows():
            # Modelo Estado
            self.actualizar_o_crear_modelo(Estados, nombre=row['Estado'])

            # Modelo Proceso
            self.actualizar_o_crear_modelo(Proceso, nombre=row['PROCESO'])

            # Modelo Asesores
            if pd.notna(row['AGENT_ID']):
                self.actualizar_o_crear_modelo(Asesores, id=row['AGENT_ID'], defaults={'nombre_completo': row['AGENT_NAME']})

            # Modelo Programa
            self.actualizar_o_crear_modelo(Programa, nombre=row['Programa académico'])

            # Modelo Sede
            self.actualizar_o_crear_modelo(Sede, nombre=row['CIUDAD'])

            # Modelo Empresa
            self.actualizar_o_crear_modelo(Empresa, nit=row['Empresa a la que se postula'])

            # Modelo Tipificación
            valor_tipificacion = self.tipificaciones.get(row['DESCRIPTION_COD_ACT'], 100.0)
            self.actualizar_o_crear_modelo(Tipificacion, nombre=row['DESCRIPTION_COD_ACT'], defaults={
                'contacto': self.contactabilidad(row),
                'valor_tipificacion': valor_tipificacion
            })

            # modelo aspirantes
            celular = row['cel_modificado']
            documento = row['Identificacion']
            nombre = row['NOMBRE']
            correo = row['CORREO']
            sede = Sede.objects.get(nombre=row['CIUDAD'])
            programa = Programa.objects.get(nombre=row['Programa académico'])
            empresa = Empresa.objects.get(nit=row['Empresa a la que se postula'])
            proceso = Proceso.objects.get(nombre=row['PROCESO'])
            estado = Estados.objects.get(nombre=row['Estado'])

            if celular in celulares_existentes or celular in celulares_a_guardar:
                aspirante_existente = Aspirantes(
                    celular=celular,
                    nombre= nombre,
                    documento=documento,
                    correo=correo,
                    sede=sede,
                    programa=programa,
                    empresa=empresa,
                    proceso=proceso,
                    estado=estado
                )
                if pd.notna(nombre):
                    aspirantes_a_actualizar.append(aspirante_existente)
            else:
                # Crear un nuevo aspirante
                nuevo_aspirante = Aspirantes(
                    celular=celular,
                    nombre= nombre,
                    documento=documento,
                    correo=correo,
                    sede=sede,
                    programa=programa,
                    empresa=empresa,
                    proceso=proceso,
                    estado=estado
                )
                aspirantes_a_crear.append(nuevo_aspirante)
                celulares_a_guardar.add(celular)

        #Inserción y actualizacion en bloque
        if aspirantes_a_crear:
            Aspirantes.objects.bulk_create(aspirantes_a_crear)
        if aspirantes_a_actualizar:
            Aspirantes.objects.bulk_update(aspirantes_a_actualizar, ['nombre', 'documento', 'correo', 'sede', 'programa', 'empresa', 'proceso', 'estado'])

        #segundo bucle para llenar las gestiones
        for index, row in df.iterrows():
            # Modelo Gestiones
            if pd.notna(row['DATE']) and pd.notna(row['DESCRIPTION_COD_ACT']) and pd.notna(row['AGENT_NAME']):
                try:
                    aspirante = Aspirantes.objects.get(celular=row['cel_modificado'])
                    tipificacion = Tipificacion.objects.get(nombre=row['DESCRIPTION_COD_ACT'])
                    asesor = Asesores.objects.get(id=row['AGENT_ID'])
                    tipo_gestion = self.validar_tipo_gestion(row, df)
                    fecha_convertida = self.convertir_fecha(row['DATE'])
                    observaciones = row['COMMENTS']
                    empresa = row['Empresa a la que se postula']
                    tiempo_gestion = row['segundos']
                    
                    # Verificar que todos los datos necesarios están disponibles
                    gestion_existente = Gestiones.objects.filter(
                        cel_aspirante=aspirante,
                        fecha=fecha_convertida,
                        tipo_gestion=tipo_gestion,
                        observaciones=observaciones,
                        tipificacion=tipificacion,
                        asesor=asesor,
                        tiempo_gestion= tiempo_gestion
                    ).exists()

                    if not gestion_existente:
                        nueva_gestion = Gestiones(
                            cel_aspirante=aspirante,
                            fecha=fecha_convertida,
                            tipo_gestion=tipo_gestion,
                            observaciones=observaciones,
                            tipificacion=tipificacion,
                            asesor=asesor,
                            empresa=empresa,
                            tiempo_gestion=tiempo_gestion
                        )
                        gestiones_a_guardar.append(nueva_gestion)
                    else:
                        print(f"la gestión ya existe para el celular: {row['cel_modificado']}.")
                except Aspirantes.DoesNotExist:
                    print(f"Aspirante con celular {row['cel_modificado']} no encontrado.")
                except Tipificacion.DoesNotExist:
                    print(f"Tipificación con código {row['DESCRIPTION_COD_ACT']} no encontrada.")
                except Asesores.DoesNotExist:
                    print(f"Asesor con ID {row['AGENT_ID']} no encontrado.")
                except Exception as e:
                    print(f"Error procesando la fila: {e}")
            else:
                continue
        

        # Actualizar estados de todos los aspirantes
        if gestiones_a_guardar:
            Gestiones.objects.bulk_create(gestiones_a_guardar)
            
        self.actualizar_estados_aspirantes()
        print("carga completada")
