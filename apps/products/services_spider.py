from config.settings.config_common import \
    LOTUS_SINGLE_PRODUCT_API_URL_PREFIX, \
    LOTUS_PRODUCTS_BY_CATALOG_API_URL_PREFIX, \
    LOTUS_STORE_PITTS, \
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, \
    LOGTAIL_SOURCE_TOKEN, \
    DYNAMIC_SYS_SETTINGS_LOCKER_SPIDER_ASYNC_PROCESS, \
    DYNAMIC_SYS_SETTINGS_SPIDER_PRODUCT_PROCESS_CATALOG_IDS, \
    DYNAMIC_SYS_SETTINGS_SPIDER_PRODUCT_PROCESS_START_INDEX, \
    DYNAMIC_SYS_SETTINGS_SPIDER_PRODUCT_PROCESS_BATCH_SIZE
from apps.products.services_es import ESProcessor
from apps.products.services_neo4j import Neo4jProcessor
from apps.commons.tools import CommonTools
from apps.products.models_mongo import MongoProductModel, MongoSkuModel
import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
import jsonpickle
from celery import shared_task
import datetime
import uuid
import boto3
import boto3.s3
import urllib3
from logtail import LogtailHandler
import logging
from PIL import Image

handler = LogtailHandler(source_token=LOGTAIL_SOURCE_TOKEN)
logger = logging.getLogger(__name__)
logger.handlers = []
logger.addHandler(handler)

class SpiderProductSelenium:
    def wait_for_ajax(driver):
        wait = WebDriverWait(driver, 15)
        try:
            wait.until(lambda driver: driver.execute_script(
                'return jQuery.active') == 0)
            wait.until(lambda driver: driver.execute_script(
                'return document.readyState') == 'complete')
        except Exception as e:
            pass

    def get_html_from_url_selenium(url):
        browser = webdriver.Chrome(ChromeDriverManager().install())
        SpiderProductSelenium.wait_for_ajax(browser)
        browser.get('https://www.zgomart.com/static/mall_pc/#/goods/2')
        return browser.page_source

class SpiderProductAPI:
    def img_compression(img_path):
        image = Image.open(img_path)
        image.thumbnail((260,300),Image.ANTIALIAS)
        image.save(img_path)

    def get_json_from_api(api_url):
        cookies = {'storeId': str(LOTUS_STORE_PITTS)}
        res = requests.get(api_url, stream=True, cookies=cookies)
        json = jsonpickle.decode(res.text)
        if json['msg'] == 'success':
            return json

    def save_product_array_json_into_mongoDB(json_array, created_datetime, version_number):
        for json_product in json_array['data']:
            
            if json_product['id'] is not None:
                product_number = json_product['id']
            elif json_product['ID'] is not None:
                product_number = json_product['ID']
            
            url = LOTUS_SINGLE_PRODUCT_API_URL_PREFIX + str(json_product['id'])
            logger.info("spider extract product(single) from url: " + url)
            single_product_json = SpiderProductAPI.get_json_from_api(url)
            if single_product_json is not None and single_product_json['data'] is not None and not CommonTools.check_is_empty(single_product_json['data']['id']):
                SpiderProductAPI.save_product_json_into_mongoDB(single_product_json['data'], created_datetime, version_number)
      
    def save_product_json_into_mongoDB(json, created_datetime, version_number):
        if json is not None and not CommonTools.check_is_empty(json['id']) and not CommonTools.check_is_empty(json['NameEn']):        
            product_origin = MongoProductModel.objects(product_number=str(json['id']))
            if product_origin is not None and len(product_origin) > 0:
                product = product_origin[0]
                Neo4jProcessor.sync_product_into_neo4j(product)

                
                logger.info("[neo4j_insert] insert product into neo4j, product_number: " + str(json['id']))
                if not CommonTools.check_is_empty(json['GoodsCategory']) and \
                        not CommonTools.check_is_empty(json['GoodsCategory']['Father']) and \
                        not CommonTools.check_is_empty(json['GoodsCategory']['Father']['Father']) and \
                        not CommonTools.check_is_empty(json['GoodsCategory']['Father']['Father']['id']):
                    if str(json['GoodsCategory']['Father']['Father']['id']) not in product['catalog_id_array']:
                        product['catalog_id_array'].append(CommonTools.format_content(str(json['GoodsCategory']['Father']['Father']['id'])))
                        
                        if json['GoodsCategory']['NameEn'] not in product['keyword_array']:
                            product['keyword_array'].append(CommonTools.format_content(json['GoodsCategory']['NameEn'])) 
                        
                        product.save()
                        logger.info("[mongoDB_update] catalog is not in the product, catalog id: " + str(json['GoodsCategory']['Father']['Father']['id']) + ", product_number: " + str(json['id']))
                    else:
                        logger.info("[mongoDB_update] catalog is already in the product, catalog id: " + str(json['GoodsCategory']['Father']['Father']['id']) + ", product_number: " + str(json['id']))
            else:   
                product = MongoProductModel(
                    product_number=str(json['id']),
                    name=CommonTools.format_content(json['NameEn']),
                    publish_status=1,
                    original_price=float(json['Price'])/100 if not CommonTools.check_is_empty(json['Price']) else 0,
                    current_price=float(json['MemberPrice'])/100 if not CommonTools.check_is_empty(json['MemberPrice']) and json['MemberPrice'] > 0 else (float(json['Price'])/100 if not CommonTools.check_is_empty(json['Price']) else 0),
                    stock=100,
                    safe_stock=5,
                    keyword_array=[
                    ],
                    created_time=created_datetime,
                    updated_time=created_datetime,
                    created_user_id="1",
                    updated_user_id="1",
                    avg_star=3.00,
                    changed_flag=1,
                    sales_rank=0,
                    sku_array=[
                        MongoSkuModel(
                            sku_number=str(json['id']),
                            attr_array=[

                            ],
                            sattr_array=[
                            ]
                        )
                    ],
                    review_array=[

                    ],
                    tag_array=[
                        'new'
                    ],
                    source='baihe',
                    version=version_number,
                    type='no_attr'
                )
                if not CommonTools.check_is_empty(json['NameZh']):
                    product['chinese_name'] = CommonTools.format_content(json['NameZh'])
                    
                if not CommonTools.check_is_empty(json['GoodsCategory']) and not CommonTools.check_is_empty(json['GoodsCategory']['Father']) and not CommonTools.check_is_empty(json['GoodsCategory']['Father']['Father']) and not CommonTools.check_is_empty(json['GoodsCategory']['Father']['Father']['id']):
                    product['catalog_id_array'].append(CommonTools.format_content(str(json['GoodsCategory']['Father']['Father']['id'])))
                    
                if not CommonTools.check_is_empty(json['Brand']) and not CommonTools.check_is_empty(json['Brand']['NameEn']):
                    product['brand'] = CommonTools.format_content(json['Brand']['NameEn'])
                else:
                    product['brand'] = 'other'
                    
                if not CommonTools.check_is_empty(json['SrcPlace'] ):
                    product['tag_array'].append(CommonTools.format_content(json['SrcPlace']))
                    
                if not CommonTools.check_is_empty(json['GoodsCategory']) and not CommonTools.check_is_empty(json['GoodsCategory']['NameEn']):
                    product['keyword_array'].append(CommonTools.format_content(json['GoodsCategory']['NameEn']))
                    
                if not CommonTools.check_is_empty(json['DescEn']):
                    product['description'] = CommonTools.format_content(json['DescEn'])
                    
                if not CommonTools.check_is_empty(json['Imgs']):
                    product['main_img'] = str(json['id']) + '.' + json['Imgs'].split(',')[0].split('.')[-1]
                    counter = 0
                    for img_url in json['Imgs'].split(','):
                        if counter > 0:
                            img_file_name = str(json['id']) + '_' + str(counter) + '.' + img_url.split('.')[-1]
                        else:
                            img_file_name = str(json['id']) + '.' + img_url.split('.')[-1]
                        SpiderProductAPI.upload_product_img_into_s3(img_url, img_file_name)
                        product['other_img_array'].append(img_file_name)
                        counter = counter + 1
                    
                if not CommonTools.check_is_empty(json['SalesVolume']):
                    if json['SalesVolume'] > 500:
                        product['tag_array'].append('bestseller')
                    elif json['SalesVolume'] > 100:
                        product['tag_array'].append('hot')

                    product['sales'] = json['SalesVolume']
                
                product.save()
                logger.info("[mongoDB_insert] insert product into mongoDB, product_number: " + str(json['id']))

                Neo4jProcessor.sync_product_into_neo4j(product)
                logger.info("[neo4j_insert] insert product into neo4j, product_number: " + str(json['id']))

    def create_product_from_lotus(catalog_id, created_datetime, version_number):
        start_index = int(CommonTools.query_settings_by_key(DYNAMIC_SYS_SETTINGS_SPIDER_PRODUCT_PROCESS_START_INDEX))
        batch_size = int(CommonTools.query_settings_by_key(DYNAMIC_SYS_SETTINGS_SPIDER_PRODUCT_PROCESS_BATCH_SIZE))
        end_index = start_index + batch_size
        
        try: 
            url = LOTUS_PRODUCTS_BY_CATALOG_API_URL_PREFIX + "?offset=" + str(start_index) + "&limit=" + str(batch_size) + "&filter={\"GoodsCategory__Father__Father__ID\":" + str(catalog_id) +  "}&action=goods_all"
            logger.info("spider extract product list from url: " + url)
    
            json = SpiderProductAPI.get_json_from_api(url)
            logger.info("catalog id: " + catalog_id + ", product count: " + str(len(json['data'])))
            SpiderProductAPI.save_product_array_json_into_mongoDB(json, created_datetime, version_number)
        except Exception as e:
            logger.error(str(e))
        
        return {"catalog_id": catalog_id, "start_index": start_index, "end_index": end_index}

    def upload_product_img_into_s3(img_url, img_file_name):
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name='us-east-2')
        key = 'products/' + img_file_name
        try:
            obj = s3.get_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key=key)

            thumbnail_key = 'products_thumbnail/' + img_file_name
            try:
                obj = s3.get_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key=thumbnail_key)
            except Exception as e:
                tmp_file_name = SpiderProductAPI.download_product_img(img_url)
                SpiderProductAPI.img_compression(tmp_file_name)
                s3.upload_file(tmp_file_name, AWS_STORAGE_BUCKET_NAME, ('products_thumbnail/' + img_file_name))
            
        except Exception as e:
            tmp_file_name = SpiderProductAPI.download_product_img(img_url)
            s3.upload_file(tmp_file_name, AWS_STORAGE_BUCKET_NAME, ('products/' + img_file_name))
            
            SpiderProductAPI.img_compression(tmp_file_name)
            s3.upload_file(tmp_file_name, AWS_STORAGE_BUCKET_NAME, ('products_thumbnail/' + img_file_name))

    def download_product_img(img_url):
        http = urllib3.PoolManager()
        r = http.request('GET', img_url, preload_content=False)
        suffix = img_url.split('.')[-1]
        
        with open("tmp." + suffix, 'wb') as out:
            while True:
                data = r.read(2000)
                if not data:
                    break
                out.write(data)

        r.release_conn()
        
        return "tmp." + suffix

    @shared_task
    def async_spider():
        locker_status = CommonTools.query_settings_by_key(DYNAMIC_SYS_SETTINGS_LOCKER_SPIDER_ASYNC_PROCESS)
        if locker_status == "1":
            logger.info("app-products][async-spider] spider is running")
        else: 
            try:
                logger.info("[app-products][async-spider] spider started")
        
                CommonTools.update_settings_by_key(DYNAMIC_SYS_SETTINGS_LOCKER_SPIDER_ASYNC_PROCESS, "1")
                
                catalog_ids = CommonTools.query_settings_by_key(DYNAMIC_SYS_SETTINGS_SPIDER_PRODUCT_PROCESS_CATALOG_IDS)
                
                created_datetime = datetime.datetime.now()
                version_number = uuid.uuid4().hex
                
                for catalog_id in catalog_ids.split(','):
                    res = SpiderProductAPI.create_product_from_lotus(catalog_id, created_datetime, version_number)
                    ESProcessor.add_index_from_mongo()
                    logger.info("[app-products][async-spider] spider is running, one catalog completed, catalog id: " + str(catalog_id) + ", result json: " + jsonpickle.encode(res, unpicklable=False))
                
                start_index = int(CommonTools.query_settings_by_key(DYNAMIC_SYS_SETTINGS_SPIDER_PRODUCT_PROCESS_START_INDEX))
                batch_size = int(CommonTools.query_settings_by_key(DYNAMIC_SYS_SETTINGS_SPIDER_PRODUCT_PROCESS_BATCH_SIZE))
                end_index = start_index + batch_size
                CommonTools.update_settings_by_key(DYNAMIC_SYS_SETTINGS_SPIDER_PRODUCT_PROCESS_START_INDEX, end_index)
                
                logger.info("[app-products][async-spider] spider is all completed, completed catalog ids: " + str(catalog_ids) + ", start index: " + str(start_index) + ", batch size: " + str(batch_size))
                
                 
            except Exception as e:
                logger.error("[app-products][async-spider] spider occurred error: " + str(e))
                
            CommonTools.update_settings_by_key(DYNAMIC_SYS_SETTINGS_LOCKER_SPIDER_ASYNC_PROCESS, "0")         
   
 
 
