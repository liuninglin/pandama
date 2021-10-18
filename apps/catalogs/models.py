from django.db import models

class Catalog(models.Model):
    name = models.TextField(blank=False, null=False, max_length=50)

    def __str__(self):
        return 'Catalog(id: {}, name: {})'.format(str(self.id), self.name)