from django.db import models
from django.contrib.auth.models import User

class Catalog(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(blank=True, max_length=50) 
    status = models.BooleanField(default=True)
    img = models.FileField(upload_to='catalog_img', null=True)

    created_user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='created_catalogs', null=True)
    created_time = models.DateTimeField(null=True)
    updated_user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='updated_catalogs', null=True)
    updated_time = models.DateTimeField(null=True)

    def __str__(self):
        return 'Catalog(id: {}, name: {})'.format(str(self.id), self.name)


# Catalog
# - name
# - code
# - status
# - pic
# - created_time
# - updated_time
# - created_user
# - updated_user
# - attrs_template
# [
# 	{
# 		"color": "red,blue,yellow"
# 	},
# 	{
# 		"size": "XL,L,M,S"
# 	}
# ]
