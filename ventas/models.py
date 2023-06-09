from django.db import models
from product.models import Producto
from gestioncliente.models import Cliente

class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_venta = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Venta #{self.id}"
    def calcular_total(self):
        total = sum(item.subtotal for item in self.items.all())
        return total

class ItemVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    subtotal = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"Item de Venta #{self.id}"
    
    def actualizar_stock_eliminacion(self):
        self.producto.stock += self.cantidad
        self.producto.save()
    
