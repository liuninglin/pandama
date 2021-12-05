from django.db import models
from django.contrib.auth.models import User
import os

class Customer(models.Model):
    first_name = models.CharField(default="", null=False, blank=False, max_length=50)
    last_name = models.CharField(default="", null=False, blank=False, max_length=50)
    username = models.CharField(null=False, blank=False, max_length=50)
    phone = models.CharField(default="", null=True, blank=True, max_length=50)
    email = models.CharField(null=False, blank=False, max_length=50)
    shipping_address = models.CharField(default="", null=True, blank=True, max_length=500)
    balance = models.DecimalField(default=10000, decimal_places=2, max_digits=10)
    img = models.FileField(upload_to="online-store/img/customer-img/")
    last_login_time = models.DateTimeField()
    last_login_ip = models.CharField(null=True, blank=True, max_length=50)
    password = models.CharField(null=True, blank=True, max_length=500)
    pass_salt = models.CharField(null=True, blank=True, max_length=500)

    created_user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='created_customers', null=True)
    created_time = models.DateTimeField(null=True)
    updated_user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='updated_customers', null=True)
    updated_time = models.DateTimeField(null=True)

    def img_filename(self):
        return os.path.basename(self.img.name)

class Wishlist(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, related_name='wishlists')
    product_number = models.CharField(null=False, blank=False, max_length=50)
    created_time = models.DateTimeField(null=True)
