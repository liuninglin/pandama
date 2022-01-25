from config.settings.config_common import DYNAMIC_SYS_SETTINGS_KEY
from config.settings.config_redis import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_AUTH
from config.settings.config_common import \
    DYNAMIC_SYS_SETTINGS_SPIDER_PRODUCT_PROCESS_CATALOG_IDS, \
    DYNAMIC_SYS_SETTINGS_SPIDER_PRODUCT_PROCESS_START_INDEX, \
    DYNAMIC_SYS_SETTINGS_SPIDER_PRODUCT_PROCESS_BATCH_SIZE, \
    DYNAMIC_SYS_SETTINGS_LOCKER_SPIDER_ASYNC_PROCESS, \
    DYNAMIC_SYS_SETTINGS_LOCKER_INDEX_ASYNC_PROCESS
import environ
env = environ.Env()

import redis
import os
from django.db import connection
from config.settings.base import BASE_DIR

redis_connection = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, 
                      db=REDIS_DB, password=REDIS_AUTH, decode_responses=True)


class CommonTools:
    def postgres_init():
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM catalogs_catalog")

        file_path = os.path.join(BASE_DIR / 'config/initialization/', 'sql_catalogs.sql')
        sql_statement = open(file_path).read()
        with connection.cursor() as c:
            c.execute(sql_statement)

    def redis_init():
        CommonTools.update_settings_by_key(
            DYNAMIC_SYS_SETTINGS_SPIDER_PRODUCT_PROCESS_CATALOG_IDS, 
            env.str('REDIS_SYSTEM_INIT_VALUE_SPIDER_PRODUCT_PROCESS_CATALOG_IDS', default='130,131,133,137,139,141,751,788,813,829,835,853'))
        CommonTools.update_settings_by_key(
            DYNAMIC_SYS_SETTINGS_SPIDER_PRODUCT_PROCESS_START_INDEX, 
            env.str('REDIS_SYSTEM_INIT_VALUE_SPIDER_PRODUCT_PROCESS_START_INDEX', default='0'))
        CommonTools.update_settings_by_key(
            DYNAMIC_SYS_SETTINGS_SPIDER_PRODUCT_PROCESS_BATCH_SIZE,
            env.str('REDIS_SYSTEM_INIT_VALUE_SPIDER_PRODUCT_PROCESS_BATCH_SIZE', default='5'))
        CommonTools.update_settings_by_key(
            DYNAMIC_SYS_SETTINGS_LOCKER_SPIDER_ASYNC_PROCESS,
            env.str('REDIS_SYSTEM_INIT_VALUE_LOCKER_SPIDER_ASYNC_PROCESS', default='0'))
        CommonTools.update_settings_by_key(
            DYNAMIC_SYS_SETTINGS_LOCKER_INDEX_ASYNC_PROCESS, 
            env.str('REDIS_SYSTEM_INIT_VALUE_LOCKER_INDEX_ASYNC_PROCESS', default='0'))

    def check_is_empty(str):
        if str is None or str == '':
            return True
        else:
            return False
    
    def query_settings_by_key(key):
        return redis_connection.hget(DYNAMIC_SYS_SETTINGS_KEY, key)
    
    def update_settings_by_key(key, value):
        return redis_connection.hset(DYNAMIC_SYS_SETTINGS_KEY, key, value)
    
    def format_content(content):
        if content is None:
            return ''
        else:
            return content.replace(',', '').replace('.', '').replace('&', '-').replace('?', '').replace("'", "").strip()