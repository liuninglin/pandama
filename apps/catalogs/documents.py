from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from apps.catalogs.models import Catalog

@registry.register_document
class CatalogDocument(Document):
    class Index:
        name = 'catalog'
    settings = {
        'number_of_shards': 1,
        'number_of_replicas': 0
    }
    class Django:
         model = Catalog
         fields = [
             'name',
         ]
