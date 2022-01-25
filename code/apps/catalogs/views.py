from apps.catalogs import models

def queryCatalogList():
    catalogs = list(models.Catalog.objects.all().order_by('-id'))
    return catalogs

def queryCatalogById(id):
    catalog = models.Catalog.objects.get(id=id)
    return catalog