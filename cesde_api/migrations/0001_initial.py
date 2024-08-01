# Generated by Django 5.0.7 on 2024-08-01 17:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Asesores",
            fields=[
                (
                    "documento",
                    models.CharField(max_length=15, primary_key=True, serialize=False),
                ),
                ("nombre", models.CharField(max_length=40)),
                ("apellido", models.CharField(blank=True, max_length=40, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Departamento",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=35)),
            ],
        ),
        migrations.CreateModel(
            name="Empresa",
            fields=[
                (
                    "nit",
                    models.CharField(max_length=20, primary_key=True, serialize=False),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Estados",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name="Proceso",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name="Programa",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=40)),
                ("descripcion", models.TextField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name="Tipificacion",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=40)),
                ("contacto", models.CharField(max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name="Tipo_gestion",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=12)),
            ],
        ),
        migrations.CreateModel(
            name="Ciudad",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=35)),
                (
                    "departamento",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cesde_api.departamento",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Aspirantes",
            fields=[
                (
                    "celular",
                    models.CharField(max_length=15, primary_key=True, serialize=False),
                ),
                ("nombre", models.CharField(max_length=40)),
                ("apellidos", models.CharField(max_length=40)),
                ("documento", models.CharField(max_length=15)),
                ("correo", models.CharField(max_length=50)),
                ("cel_opcional", models.CharField(blank=True, max_length=15)),
                (
                    "ciudad",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cesde_api.ciudad",
                    ),
                ),
                (
                    "empresa",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cesde_api.empresa",
                    ),
                ),
                (
                    "estado",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cesde_api.estados",
                    ),
                ),
                (
                    "proceso",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cesde_api.proceso",
                    ),
                ),
                (
                    "programa",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cesde_api.programa",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Gestiones",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("fecha", models.DateTimeField()),
                ("observaciones", models.TextField(blank=True, max_length=300)),
                (
                    "cel_aspirante",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cesde_api.aspirantes",
                    ),
                ),
                (
                    "tipificacion",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cesde_api.tipificacion",
                    ),
                ),
                (
                    "tipo_gestion",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cesde_api.tipo_gestion",
                    ),
                ),
            ],
        ),
    ]
