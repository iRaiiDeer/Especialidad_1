from django.contrib.auth.models import Group, User #importa los modelos Group y user
from django.db import models #importa los metodos necesarios para trabajar con modellos
from django.db import models

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100, null=True, blank=True, verbose_name='Nombre Proveedor')
    apellido = models.CharField(max_length=100, null=True, blank=True, verbose_name='Apellido Proveedor')
    celular = models.IntegerField()
    empresa = models.CharField(max_length=100, null=True, blank=True, verbose_name='Nombre empresa')
    descripcion=models.CharField(max_length=250, null=True, blank=True, verbose_name='Descripcion de los productos')
    correo =   models.EmailField(null=True) 
    created = models.DateTimeField(auto_now_add=True,verbose_name='Fecha Creación')
    updated = models.DateTimeField(auto_now=True,verbose_name='Fecha Actualización')
    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['nombre']   
    def __str__(self):
        return self.nombre

