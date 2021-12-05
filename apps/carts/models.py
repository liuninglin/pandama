from django.db import models
from apps.customers.models import Customer

class Cart(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, related_name='carts')
    created_time = models.DateTimeField()

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.PROTECT, related_name='cartitems')
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, related_name='cartitems')
    product_number = models.CharField(null=True, blank=True, max_length=50)
    sku_number = models.CharField(null=True, blank=True, max_length=50)
    name = models.CharField(null=True, blank=True, max_length=200) 
    main_img = models.CharField(null=True, blank=True, max_length=200) 
    original_price = models.DecimalField(default=0, decimal_places=2, max_digits=10) 
    current_price = models.DecimalField(default=0, decimal_places=2, max_digits=10) 
    qty=models.IntegerField(default=0)

    created_time = models.DateTimeField()
    updated_time = models.DateTimeField()
