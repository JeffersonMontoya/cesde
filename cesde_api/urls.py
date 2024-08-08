from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'sedes', SedeViewSet)
router.register(r'asesores' , AsesorViewSet)
router.register(r'estados', EstadoViewSet)
router.register(r'aspirantes', AspiranteViewSet)
router.register(r'aspirantes-filter', AspiranteFilterViewSet, basename='aspirantes-filter')
router.register(r'asesor',AsesoresViewSet)
router.register(r'sedes', SedeViewSet)
router.register(r'estados', EstadoViewSet)
router.register(r'tipo-gestion', TipoGestionViewSet)
router.register(r'gestiones', GestionViewSet)
router.register(r'programas', ProgramaViewSet)
router.register(r'empresas', EmpresaViewSet)
router.register(r'procesos', ProcesoViewSet )
router.register(r'tipificaciones' , TipificacionViewSet)
router.register(r'aspirantes-historico', AspiranteHistoricoView, basename='aspirantes-historico')


urlpatterns = [
    path('', include(router.urls)),
    path('cargar_csv/', Cargarcsv.as_view(), name='cargar_csv'),

]
