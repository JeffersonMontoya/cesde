# Generated by Django 5.0.7 on 2024-08-14 11:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("cesde_api", "0011_tipificacion_gestion_final_alter_gestiones_estado"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="tipificacion",
            name="gestion_final",
        ),
    ]
