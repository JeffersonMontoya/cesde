from django.db.models import Count, Avg, F, Sum
from datetime import datetime, timedelta  # Asegúrate de importar timedelta
from .models import *


def obtener_estadisticas_generales(queryset):
    # Obtener estadísticas básicas por estado y proceso
    estadisticas_basicas = queryset.values('estado__nombre').annotate(count=Count('estado')).order_by('-count')

    # Contar gestiones por tipo de contacto
    gestiones_totales = queryset.filter(gestiones__isnull=False).count()
    contactabilidad_count = queryset.filter(gestiones__tipificacion__contacto=True).count()
    no_contactabilidad_count = queryset.filter(gestiones__tipificacion__contacto=False).count()

    # Calcular los porcentajes basados en gestiones
    contactabilidad_percentage = (contactabilidad_count / gestiones_totales * 100) if gestiones_totales > 0 else 0
    no_contactabilidad_percentage = (no_contactabilidad_count / gestiones_totales * 100) if gestiones_totales > 0 else 0

    # Calcular tiempo promedio de WhatsApp en minutos
    tiempo_whatsapp_total = queryset.filter(gestiones__tipo_gestion__nombre='WhatsApp').aggregate(
        total=Sum('gestiones__tiempo_gestion')
    )['total'] or 0
    total_gestiones_whatsapp = queryset.filter(gestiones__tipo_gestion__nombre='WhatsApp').count()
    promedio_tiempo_wpp = (tiempo_whatsapp_total / 60 / total_gestiones_whatsapp) if total_gestiones_whatsapp > 0 else 0

    # Calcular tiempo promedio de llamadas en minutos
    tiempo_llamada_total = queryset.filter(gestiones__tipo_gestion__nombre='Llamada').aggregate(
        total=Sum('gestiones__tiempo_gestion')
    )['total'] or 0
    total_gestiones_llamada = queryset.filter(gestiones__tipo_gestion__nombre='Llamada').count()
    promedio_tiempo_llamada = (tiempo_llamada_total / 60 / total_gestiones_llamada) if total_gestiones_llamada > 0 else 0

    total_procesos_seleccion = queryset.filter(gestiones__tipificacion__nombre='En_proceso_de_selección').count()

    # Integrar las estadísticas adicionales en la respuesta
    estadisticas = {
        'estadisticas_basicas': list(estadisticas_basicas),
        'contactabilidad': {
            'count': contactabilidad_count,
            'percentage': round(contactabilidad_percentage, 2)
        },
        'no_contactabilidad': {
            'count': no_contactabilidad_count,
            'percentage': round(no_contactabilidad_percentage, 2)
        },
        'promedio_tiempo_whatsapp': round(promedio_tiempo_wpp, 2),
        'promedio_tiempo_llamada': round(promedio_tiempo_llamada, 2),
        'en_seleccion_total': total_procesos_seleccion
    }

    return estadisticas


def obtener_estadisticas_por_fechas(queryset, fecha_inicio, fecha_fin):
    # Si la fecha de inicio y fin son iguales, incluimos todo el día
    if fecha_inicio == fecha_fin:
        # Asegurar que la fecha fin incluya el final del día
        fecha_fin = datetime.combine(fecha_fin, datetime.max.time())
        fecha_inicio = datetime.combine(fecha_inicio, datetime.min.time())
    else:
        # Aumentar un día a la fecha de fin para incluir el último día completo
        fecha_fin = fecha_fin + timedelta(days=1)

    # Filtrar gestiones por el rango de fechas
    gestiones_filtradas = queryset.filter(fecha__range=[fecha_inicio, fecha_fin])

    # Obtener los IDs de los aspirantes relacionados con las gestiones filtradas
    aspirantes_ids = gestiones_filtradas.values_list('cel_aspirante_id', flat=True).distinct()

    # Filtrar aspirantes por los IDs obtenidos
    aspirantes_filtrados = Aspirantes.objects.filter(celular__in=aspirantes_ids)

    # Obtener estadísticas básicas por estado para los aspirantes filtrados
    estadisticas = aspirantes_filtrados.values('estado__nombre').annotate(count=Count('estado')).order_by('-count')

    return {
        'estadisticas': list(estadisticas),
    }




def obtener_contactabilidad(gestiones_queryset):
    # Total de gestiones
    gestiones_totales = gestiones_queryset.count()

    # Contar gestiones por tipo de contacto
    contactabilidad_count = gestiones_queryset.filter(tipificacion__contacto=True).count()
    no_contactabilidad_count = gestiones_queryset.filter(tipificacion__contacto=False).count()

    # Calcular porcentajes
    contactabilidad_percentage = (contactabilidad_count / gestiones_totales * 100) if gestiones_totales > 0 else 0
    no_contactabilidad_percentage = (no_contactabilidad_count / gestiones_totales * 100) if gestiones_totales > 0 else 0

    return {
        'contactabilidad': {
            'count': contactabilidad_count,
            'percentage': contactabilidad_percentage,
        },
        'no_contactabilidad': {
            'count': no_contactabilidad_count,
            'percentage': no_contactabilidad_percentage,
        },
    }