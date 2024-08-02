from django.db import models

# Create your models here.


class Departamento(models.Model):
    nombre = models.CharField(max_length=35)

    def __str__(self):
        return self.nombre


class Ciudad(models.Model):
    nombre = models.CharField(max_length=35)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre


class Estados(models.Model):
    nombre = models.CharField(max_length=15)

    def __str__(self):
        return self.nombre


class Programa(models.Model):
    nombre = models.CharField(max_length=40)
    descripcion = models.TextField(max_length=300)

    def __str__(self):
        return self.nombre


class Empresa(models.Model):
    # Definir nit como clave primaria
    nit = models.CharField(max_length=20, primary_key=True)

    def __str__(self):
        return self.nit


class Proceso(models.Model):
    nombre = models.CharField(max_length=40)
    
    def __str__(self):
        return self.nombre

class Aspirantes(models.Model):
    celular = models.CharField(max_length=15, primary_key=True)
    nombre = models.CharField(max_length=40)
    apellidos = models.CharField(max_length=40)
    documento = models.CharField(max_length=15)
    correo = models.CharField(max_length=50)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE)
    cel_opcional = models.CharField(max_length=15, blank=True)
    estado = models.ForeignKey(Estados, on_delete=models.CASCADE)
    programa = models.ForeignKey(Programa, on_delete=models.CASCADE)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    def __str__(self):
        return f" {self.nombre} {self.apellidos} {self.celular}  "



class Tipo_gestion(models.Model):
    nombre = models.CharField(max_length=12)


    def __str__(self):
        return self.nombre


class Asesores(models.Model):
    documento = models.CharField(max_length=15, primary_key=True)
    nombre = models.CharField(max_length=40)
    apellido = models.CharField(max_length=40, null=True, blank=True)

    def __str__(self):
        return f"{self.documento} - {self.nombre} {self.apellido}"


class Tipificacion(models.Model):
    nombre = models.CharField(max_length=40)
    contacto = models.CharField(max_length=2)
    
    def __str__(self):
        return self.nombre
    
class Gestiones(models.Model):
    cel_aspirante = models.ForeignKey(Aspirantes, on_delete=models.CASCADE)
    fecha = models.DateTimeField()
    tipo_gestion = models.ForeignKey(Tipo_gestion, on_delete=models.CASCADE)
    observaciones = models.TextField(max_length=300, blank=True)
    tipificacion = models.ForeignKey(Tipificacion, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.fecha} - {self.cel_aspirante.celular}"

