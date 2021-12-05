from config.settings.config_common import DYNAMIC_SYS_SETTINGS_KEY
from config.settings.config_redis import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_AUTH
import redis

redis_connection = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, 
                      db=REDIS_DB, password=REDIS_AUTH, decode_responses=True)


class CommonTools:
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