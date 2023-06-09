from django.db import models
from django.contrib.auth.models import Group, User
from product.models import Producto
from gestioncliente.models import Cliente

# Create your models here.



class Cotizacion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2,null=True)

    def __str__(self):
        return f"Cotizacion {self.id} - {self.cliente.nombre1}"
    
    def calcular_total(self):
        return sum(item.subtotal for item in self.items.all())
    


class ItemCot(models.Model):
    orden_cotizacion = models.ForeignKey(Cotizacion, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    descripcion = models.TextField(null=True)
    subtotal =  models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField(default=1)

    def calcular_subtotal(self):
        self.subtotal = self.producto.precio * self.cantidad

    
    def save(self, *args, **kwargs):
        self.calcular_subtotal()
        super().save(*args, **kwargs)   


