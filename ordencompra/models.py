from django.db import models
from django.contrib.auth.models import Group, User
from product.models import Producto
from prov.models import Proveedor

class OrdenCompra(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Orden de compra #{self.pk} - Proveedor: {self.proveedor}'

    def calcular_total(self):
        return sum(item.subtotal for item in self.items.all())


class ItemOrden(models.Model):
    orden_compra = models.ForeignKey(OrdenCompra, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def calcular_subtotal(self):
        self.subtotal = self.producto.precio * self.cantidad

    def save(self, *args, **kwargs):
        self.calcular_subtotal()
        super().save(*args, **kwargs)
