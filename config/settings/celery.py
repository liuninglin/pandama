import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()


from celery import Celery
from celery.schedules import crontab
from apps.products.services_es import ESProcessor
from apps.products.services_neo4j import Neo4jProcessor
from config.settings.config_common import LOGTAIL_SOURCE_TOKEN
from logtail import LogtailHandler
import logging
import jsonpickle

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='MQ')
app.autodiscover_tasks()

handler = LogtailHandler(source_token=LOGTAIL_SOURCE_TOKEN)
logger = logging.getLogger(__name__)
logger.handlers = []
logger.addHandler(handler)

app.conf.beat_schedule = {
    'es-add-index-every-hour': {
        'task': 'tasks.task_es_add_index',
        'schedule': crontab(minute=0, hour="*/1")
    },
    'neo4j-add-order-every-hour': {
        'task': 'tasks.task_neo4j_add_order',
        'schedule': crontab(minute=0, hour="*/1")
    }
}
app.conf.timezone = 'US/Eastern'

@app.task
def task_es_add_index():
    res_array = ESProcessor.add_index_from_mongo()
    logger.info("[sync product from mongo to es] job completed \n" + jsonpickle.encode(res_array, unpicklable=False))

@app.task
def task_neo4j_add_order():
    res_array = Neo4jProcessor.sync_order_from_db()
    logger.info("[sync order from db to neo4j] job completed \n" + jsonpickle.encode(res_array, unpicklable=False))
    