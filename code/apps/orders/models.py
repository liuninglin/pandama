from django.db import models
from apps.customers.models import Customer

class Order(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, related_name='orders')
    created_time = models.DateTimeField()

    customer_firstname = models.CharField(null=True, blank=True, max_length=50)
    customer_lastname = models.CharField(null=True, blank=True, max_length=50)
    customer_phone = models.CharField(null=True, blank=True, max_length=50)
    customer_email = models.CharField(null=True, blank=True, max_length=50)
    customer_shipping_address = models.CharField(null=True, blank=True, max_length=500)
    
    total_price = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    #0:packaging 1:shipping 2:Delivered
    status = models.IntegerField(default = 0)

    sync_flag = models.BooleanField(default=False) # True: sync to neo4j, False: not sync to neo4j

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='orderitems')
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    
    # product = Product_Sku_DTO
    product_number = models.CharField(null=True, blank=True, max_length=50)
    product_sku = models.CharField(null=True, blank=True, max_length=50)
    product_name = models.CharField(null=True, blank=True, max_length=200) 
    product_img = models.CharField(null=True, blank=True, max_length=200) 
    product_original_price = models.DecimalField(default=0, decimal_places=2, max_digits=10) 
    product_current_price = models.DecimalField(default=0, decimal_places=2, max_digits=10) 
    amount=models.IntegerField(default=0)
    created_time = models.DateTimeField()

    redundant_product_info_json = models.TextField(null=True, blank=True, max_length=1000)
    # 0:packaging 1:shipping 2:Delivered
    status = models.IntegerField(default=0)
    version = models.CharField(null=True, blank=True, max_length=50)
    screen_shot = models.CharField(null=True, blank=True, max_length=200)
    catalog_id_array = models.CharField(null=True, blank=True, max_length=500)
