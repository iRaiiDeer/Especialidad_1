# Generated by Django 2.0.2 on 2023-06-06 04:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotizacion', '0006_remove_cotizacion_archivo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cotizacion',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='itemcot',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
