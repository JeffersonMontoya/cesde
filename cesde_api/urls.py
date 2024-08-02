from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EstadoViewSet, SedeViewSet , 
    TipoGestionViewSet, AsesorViewSet, GestionViewSet, ProgramaViewSet, 
    EmpresaViewSet, Cargarcsv , AspiranteViewSet, ProcesoViewSet , TipificacionViewSet
)

router = DefaultRouter()
router.register(r'sedes', SedeViewSet)
router.register(r'estados', EstadoViewSet)
router.register(r'aspirantes', AspiranteViewSet)
router.register(r'tipo-gestion', TipoGestionViewSet)
router.register(r'asesores', AsesorViewSet)
router.register(r'gestiones', GestionViewSet)
router.register(r'programas' , ProgramaViewSet)
router.register(r'empresas' , EmpresaViewSet)
router.register(r'procesos', ProcesoViewSet )
router.register(r'tipificaciones' , TipificacionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('cargar_csv/', Cargarcsv.as_view(), name='cargar_csv'),

]
