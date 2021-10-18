from django.http.response import HttpResponse
from django.shortcuts import render
from django.core.cache import cache
from django_redis import get_redis_connection
from apps.catalogs import models
from apps.catalogs.documents import CatalogDocument

def tearDown(self):
    model = models.Catalog(name='2')
    # storing data into MongoDB
    model.save()

    # Redis operation
    res = cache.keys('*')

    s = CatalogDocument.search().filter("term", name="2")

    return HttpResponse(s)
