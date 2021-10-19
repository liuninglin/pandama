from django.http.response import HttpResponse
from django.shortcuts import render
from django.core.cache import cache
from django_redis import get_redis_connection
from apps.catalogs import models
from apps.catalogs.documents import CatalogDocument
from celery import shared_task

@shared_task
def asynCall():
    model = models.Catalog(name='async')
    model.save(using="mongoDB")

def test_asyncCall():
    asynCall()
    return HttpResponse("asyn done")

def test_redis():
    res = cache.keys('*') 
    return HttpResponse("redis keys:" + res)

def test_mongoDB():
    model = models.Catalog(name='shoes')
    model.save(using="mongoDB")
    return HttpResponse("mongoDB save success")

def test_es():
    s = CatalogDocument.search().filter("term", name="2")
    return HttpResponse("elasticsearch result:" + s)