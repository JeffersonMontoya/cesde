# Generated by Django 5.1 on 2024-08-18 19:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cesde_api", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="asesores",
            old_name="documento",
            new_name="id",
        ),
        migrations.RemoveField(
            model_name="asesores",
            name="apellido",
        ),
        migrations.RemoveField(
            model_name="asesores",
            name="nombre",
        ),
        migrations.RemoveField(
            model_name="aspirantes",
            name="apellidos",
        ),
        migrations.RemoveField(
            model_name="aspirantes",
            name="cel_opcional",
        ),
        migrations.RemoveField(
            model_name="programa",
            name="descripcion",
        ),
        migrations.AddField(
            model_name="asesores",
            name="nombre_completo",
            field=models.CharField(default=1, max_length=70),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="gestiones",
            name="asesor",
            field=models.ForeignKey(
                default="null",
                on_delete=django.db.models.deletion.CASCADE,
                to="cesde_api.asesores",
            ),
        ),
        migrations.AddField(
            model_name="tipificacion",
            name="valor_tipificacion",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name="aspirantes",
            name="estado",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="cesde_api.estados",
            ),
        ),
        migrations.AlterField(
            model_name="aspirantes",
            name="nombre",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name="gestiones",
            name="fecha",
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name="programa",
            name="nombre",
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name="tipificacion",
            name="contacto",
            field=models.BooleanField(default=False),
        ),
    ]
