from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'departamentos', DepartamentoViewSet)
router.register(r'ciudades', CiudadViewSet)
router.register(r'estados', EstadoViewSet)
router.register(r'aspirantes', AspiranteViewSet)
router.register(r'tipo-gestion', TipoGestionViewSet)
router.register(r'asesores', AsesorViewSet)
router.register(r'gestiones', GestionViewSet)
router.register(r'programas' , ProgramaViewSet)
router.register(r'empresas' , EmpresaViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('cargar_csv/', Cargarcsv.as_view(), name='cargar_csv')
]
