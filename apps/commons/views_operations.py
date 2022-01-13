from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from apps.products.services_mongo import MongoProcessor
from apps.products.services_neo4j import Neo4jProcessor
from apps.products.services_es import ESProcessor
from apps.products.services_spider import SpiderProductAPI
from apps.carts.views import clear_all_sessions
from apps.catalogs.views import queryCatalogList
from config.settings.config_common import \
    LOGTAIL_SOURCE_TOKEN, \
    DYNAMIC_SYS_SETTINGS_LOCKER_SPIDER_ASYNC_PROCESS, \
    DYNAMIC_SYS_SETTINGS_SPIDER_PRODUCT_PROCESS_CATALOG_IDS, \
    DYNAMIC_SYS_SETTINGS_SPIDER_PRODUCT_PROCESS_START_INDEX, \
    DYNAMIC_SYS_SETTINGS_SPIDER_PRODUCT_PROCESS_BATCH_SIZE, \
    DYNAMIC_SYS_SETTINGS_LOCKER_INDEX_ASYNC_PROCESS
from apps.commons.tools import CommonTools
from django.http import HttpResponseForbidden    
from logtail import LogtailHandler
import logging

handler = LogtailHandler(source_token=LOGTAIL_SOURCE_TOKEN)
logger = logging.getLogger(__name__)
logger.handlers = []
logger.addHandler(handler)


class ManualOperationPageView:
    @csrf_exempt
    def es_delete_all_index(request):
        if request.method == "POST":
            ESProcessor.delete_all_index()
            logger.info("[app-products] es index deleted")
            return HttpResponse("es index deleted")
    
    @csrf_exempt
    def mongo_delete_all_data(request):
        if request.method == "POST":
            MongoProcessor.delete_all_products()
            logger.info("[app-products] mongoDB all products deleted")
            return HttpResponse("mongoDB all products deleted")
    
    @csrf_exempt
    def es_create_mapping(request):
        if request.method == "POST":
            res = ESProcessor.create_mapping()
            return HttpResponse(res)
    
    @csrf_exempt
    def spider_execute(requset):
        if requset.method == "POST":
            locker_status = CommonTools.query_settings_by_key(DYNAMIC_SYS_SETTINGS_LOCKER_SPIDER_ASYNC_PROCESS)
            if locker_status == "0": 
                SpiderProductAPI.async_spider.delay() 
            
                catalog_ids = CommonTools.query_settings_by_key(DYNAMIC_SYS_SETTINGS_SPIDER_PRODUCT_PROCESS_CATALOG_IDS)
                start_index = int(CommonTools.query_settings_by_key(DYNAMIC_SYS_SETTINGS_SPIDER_PRODUCT_PROCESS_START_INDEX))
                batch_size = int(CommonTools.query_settings_by_key(DYNAMIC_SYS_SETTINGS_SPIDER_PRODUCT_PROCESS_BATCH_SIZE))
            
                return HttpResponse("Async spider process started, please wait......\nCatalog Ids: " + str(catalog_ids) + "\nStart Index: " + str(start_index) + "\nBatch Size: " + str(batch_size))
            else:
                return HttpResponse("Spider process is running, please wait......")
    
    @csrf_exempt
    def es_add_index(request):
        if request.method == "POST":
            locker_status = CommonTools.query_settings_by_key(DYNAMIC_SYS_SETTINGS_LOCKER_INDEX_ASYNC_PROCESS)
            if locker_status == "0":    
                ESProcessor.async_es_index.delay() 
                return HttpResponse("Async es index started, please wait......")
            else:
                return HttpResponse("Es index process is running, please wait......")

    @csrf_exempt
    def neo4j_sync_orders(request):
        if request.method == "POST":
            Neo4jProcessor.sync_order_from_db.delay() 
            return HttpResponse("Sync orders to Neo4j.....")

    @csrf_exempt
    def clear_all_sessions(request):
        if request.method == "POST":
            clear_all_sessions()
            return HttpResponse("All sessions cleared")
            