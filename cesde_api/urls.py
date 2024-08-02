from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
<<<<<<< HEAD
    DepartamentoViewSet, CiudadViewSet, EstadoViewSet,
    AspiranteViewSet, AspiranteFilterViewSet, TipoGestionViewSet,
    AsesorViewSet, GestionViewSet, ProgramaViewSet, EmpresaViewSet,
    Cargarcsv
=======
    EstadoViewSet, SedeViewSet , 
    TipoGestionViewSet, AsesorViewSet, GestionViewSet, ProgramaViewSet, 
    EmpresaViewSet, Cargarcsv , AspiranteViewSet, ProcesoViewSet , TipificacionViewSet
>>>>>>> 6b5feeb6037ee90671e8064a9e53756979f73c0d
)

router = DefaultRouter()
router.register(r'sedes', SedeViewSet)
router.register(r'estados', EstadoViewSet)
router.register(r'aspirantes', AspiranteViewSet)
router.register(r'aspirantes-filter', AspiranteFilterViewSet, basename='aspirantes-filter')
router.register(r'tipo-gestion', TipoGestionViewSet)
router.register(r'asesores', AsesorViewSet)
router.register(r'gestiones', GestionViewSet)
<<<<<<< HEAD
router.register(r'programas', ProgramaViewSet)
router.register(r'empresas', EmpresaViewSet)
=======
router.register(r'programas' , ProgramaViewSet)
router.register(r'empresas' , EmpresaViewSet)
router.register(r'procesos', ProcesoViewSet )
router.register(r'tipificaciones' , TipificacionViewSet)
>>>>>>> 6b5feeb6037ee90671e8064a9e53756979f73c0d

urlpatterns = [
    path('', include(router.urls)),
    path('cargar_csv/', Cargarcsv.as_view(), name='cargar_csv'),

]
