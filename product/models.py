from django.db import models
from prov.models import Proveedor
from categoria.models import Categoria

class Producto(models.Model):
    proveedor=models.ManyToManyField(Proveedor)
    nombre = models.CharField(max_length=100)
    precio = models.IntegerField()
    descripcion = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    talla = models.CharField(max_length=4)
    stock=models.IntegerField()

    def __str__(self):
        return self.nombre
