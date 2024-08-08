from django.db.models import Count

def obtener_estadisticas_generales(queryset):
    return queryset.values('proceso__nombre','estado__nombre').annotate(count=Count('estado')).order_by('-count')


