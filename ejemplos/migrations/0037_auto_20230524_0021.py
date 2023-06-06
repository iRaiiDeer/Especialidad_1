# Generated by Django 2.0.2 on 2023-05-24 04:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ejemplos', '0036_auto_20230524_0013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordencompra',
            name='fecha_creacion',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='ordencompra',
            name='proveedor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ejemplos.Proveedor'),
        ),
    ]
