# Generated by Django 5.0.7 on 2024-08-26 12:57

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
                    "id",
                    models.CharField(max_length=15, primary_key=True, serialize=False),
                ),
                ("nombre_completo", models.CharField(max_length=70)),
            ],
        ),
        migrations.CreateModel(
            name="Empresa",
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
                ("nit", models.CharField(max_length=50)),
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
                ("nombre", models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name="Sede",
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
                ("contacto", models.BooleanField(default=False)),
                (
                    "valor_tipificacion",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
                ),
                (
                    "categoria",
                    models.CharField(
                        choices=[
                            ("Interesado", "Interesado"),
                            ("En seguimiento", "En seguimiento"),
                            ("No contactado", "No contactado"),
                            ("Descartado", "Descartado"),
                            ("Opcional", "Opcional"),
                        ],
                        default="Opcional",
                        max_length=50,
                    ),
                ),
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
            name="Aspirantes",
            fields=[
                (
                    "celular",
                    models.CharField(max_length=15, primary_key=True, serialize=False),
                ),
                ("nombre", models.CharField(max_length=100)),
                ("documento", models.CharField(max_length=15)),
                ("correo", models.CharField(max_length=50)),
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
                        default=1,
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
                (
                    "sede",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="cesde_api.sede"
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
                    "asesor",
                    models.ForeignKey(
                        default="null",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cesde_api.asesores",
                    ),
                ),
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
