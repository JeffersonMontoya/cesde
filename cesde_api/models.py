from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models


class Sede(models.Model):
    nombre = models.CharField(max_length=35)

    def __str__(self):
        return self.nombre

class Estados(models.Model):
    nombre = models.CharField(max_length=25)

    def __str__(self):
        return self.nombre

class Programa(models.Model):
    nombre = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre

class Empresa(models.Model):
    nit = models.CharField(max_length=70)

    def __str__(self):
        return self.nit

class Proceso(models.Model):
    nombre = models.CharField(max_length=40)

    def __str__(self):
        return self.nombre


class Aspirantes(models.Model):
    celular = models.CharField(max_length=15, primary_key=True)
    nombre = models.CharField(max_length=100)
    documento = models.CharField(max_length=15)
    correo = models.CharField(max_length=100)
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE)
    programa = models.ForeignKey(Programa, on_delete=models.CASCADE)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    proceso = models.ForeignKey(Proceso, on_delete=models.CASCADE)
    estado = models.ForeignKey(Estados, on_delete=models.CASCADE, default=1)
    fecha_ingreso = models.CharField(max_length=30, default='Octubre')
    fecha_modificacion = models.DateField(blank=True, null=True, default=None)
    detalle = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre} {self.celular}"

class Tipo_gestion(models.Model):
    nombre = models.CharField(max_length=12)

    def __str__(self):
        return self.nombre

class Asesores(models.Model):
    id = models.CharField(max_length=15, primary_key=True)
    nombre_completo = models.CharField(max_length=70)

    def __str__(self):
        return f"{str(self.id)} - {self.nombre_completo}"

class Tipificacion(models.Model):
    nombre = models.CharField(max_length=40)
    contacto = models.BooleanField(default=False)
    valor_tipificacion = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    categoria = models.CharField(max_length=50, choices=[
        ('Interesado', 'Interesado'),
        ('En seguimiento', 'En seguimiento'),
        ('No contactado', 'No contactado'),
        ('Descartado', 'Descartado'),
        ('Opcional', 'Opcional'),
    ], default='Opcional')

    def save(self, *args, **kwargs):
        self.categoria = self.asignar_categoria()
        super().save(*args, **kwargs)

    def asignar_categoria(self):
        categorias = {
            'Interesado': ['Matriculado', 'Liquidacion', 'En_proceso_de_selección', 'Interesado_en_seguimiento'],
            'En seguimiento': ['Volver_a_llamar'],
            'No contactado': ['Primer_intento_de_contacto', 'Segundo_intento_de_contacto', 'Tercer_intento_de_contacto', 'Fuera_de_servicio'],
            'Descartado': ['Número_inválido', 'Imposible_contacto', 'Por_ubicacion', 'No_Manifiesta_motivo', 'Proxima_convocatoria', 'Eliminar_de_la_base', 'Sin_perfil', 'Sin_tiempo', 'Sin_interes', 'Ya_esta_estudiando_en_otra_universidad', 'Otra_area_de_interés', 'Otra_area_de_interes'],
        }

        for categoria, tipificaciones in categorias.items():
            if self.nombre in tipificaciones:
                return categoria
        return 'Opcional'

    def __str__(self):
        return self.nombre
    
    
class Gestiones(models.Model):
    cel_aspirante = models.ForeignKey(Aspirantes, on_delete=models.CASCADE)
    fecha = models.DateTimeField()
    tipo_gestion = models.ForeignKey(Tipo_gestion, on_delete=models.CASCADE)
    observaciones = models.TextField(max_length=300, blank=True)
    tipificacion = models.ForeignKey(Tipificacion, on_delete=models.CASCADE)
    asesor = models.ForeignKey(Asesores , on_delete=models.CASCADE  , default = 'null')
    empresa = models.CharField(max_length=120)
    tiempo_gestion = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.fecha} - {self.cel_aspirante.celular}"


class LoginAttempt(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    attempts = models.IntegerField(default=0)
    last_attempt = models.DateTimeField(auto_now_add=True)
    permanently_blocked = models.BooleanField(default=False)  # Campo para bloquear permanentemente

    def reset_attempts(self):
        self.attempts = 0
        self.last_attempt = timezone.now()
        self.save()

    def increment_attempts(self):
        self.attempts += 1
        self.last_attempt = timezone.now()
        self.save()
        
    def __str__(self):
        return f"{self.user} - {self.attempts}"
