# Generated by Django 5.1 on 2024-09-16 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cesde_api", "0004_alter_estados_nombre"),
    ]

    operations = [
        migrations.AlterField(
            model_name="estados",
            name="nombre",
            field=models.CharField(max_length=25),
        ),
    ]
