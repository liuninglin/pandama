from django.shortcuts import get_object_or_404, render
from django.http.response import HttpResponse
from django.utils import timezone
from mongoengine.base import metaclasses
import redis
from apps.carts.models import CartItem, Cart
from apps.customers.models import Customer
from config.settings.config_redis import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_AUTH
from config.settings.config_common import LOGTAIL_SOURCE_TOKEN
from celery import shared_task
from apps.products.services_mongo import MongoProcessor
from apps.carts.documents_redis import CartItem_DTO

from logtail import LogtailHandler
import logging
handler = LogtailHandler(source_token=LOGTAIL_SOURCE_TOKEN)
logger = logging.getLogger(__name__)
logger.handlers = []
logger.addHandler(handler)

redis_connection = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, 
                      db=REDIS_DB, password=REDIS_AUTH, decode_responses=True)

def clear_all_sessions():
    cursor = '0'
    while cursor != 0:
        cursor, data = redis_connection.scan(cursor, ":1:django.contrib*", 1000)
        for key in data:
            redis_connection.delete(key)
            

def queryCartByCustomerId(customerId):
    res_redis = queryCartByCustomerId_Redis(customerId)
    if res_redis == "error":
        res_redis = queryCartByCustomerId_RDBMS(customerId)
        if res_redis["skus"] != []:
            # Sync data to redis
            syncCart_Redis(customerId)
    return res_redis
    

def queryCartByCustomerId_Redis(customerId):
    try:
        carts_dicc = redis_connection.hgetall("cart:common:" + str(customerId))
    except:
        return "error"
    # Find all the sku number
    carts_skus = list(set([key.split(":")[-1] for key in list(carts_dicc.keys())]))
    # Query the latest information of the sku from MongoDB
    carts_sku_info_list = []

    if len(carts_dicc) > 0:
        carts_info = MongoProcessor.query_sku_array_by_sku_number_array(carts_skus)
        if carts_info != None:
            for sku in carts_info:
                qty = int(carts_dicc["product_qty:" + sku.sku_number])
                newsku = CartItem_DTO(sku, qty)
                carts_sku_info_list.append(newsku)
    else:
        carts_res = {"skus": [], "total": 0}
        return carts_res
        
    total_price = 0

    for sku in carts_sku_info_list:
        qty = sku.qty
        total_price = total_price + sku.current_price * qty
    
    carts_res = {"skus":carts_sku_info_list, "total":total_price}

    return carts_res


def queryCartByCustomerId_RDBMS(customerId):
    try:
        customer = Customer.objects.get(id = customerId)
        cartitems = CartItem.objects.filter(customer = customer)
    except:
        return {"skus": [], "total": 0}

    total_price = 0

    for sku in cartitems:
        try:
            total_price += sku.qty * sku.current_price
        except:
            continue
    
    return {"skus": cartitems, "total" : total_price}


def addCart(customerId, skuId, qty):
    message = addCart_Redis(customerId, skuId, qty)
    if message["status"] == 200:
        async_RDBMS.delay(customerId, skuId, qty)
        # async_RDBMS(customerId, skuId, qty)
    return message


def addCart_Redis(customerId, skuId, qty):
    qty = int(qty)
    try:
        if redis_connection.hexists("cart:common:" + str(customerId), "product_qty:" + skuId):
            curr_qty = int(redis_connection.hget("cart:common:" + str(customerId), "product_qty:" + skuId))
            qty = curr_qty + qty
        else:
            sku = MongoProcessor.query_sku_array_by_sku_number_array([str(skuId)])[0]
            sku_info = "{product_number:" + sku.product_number + ",sku_number:" + sku.sku_number + ",name:" + sku.name + \
                        ",main_img:" + sku.main_img + ",original_price:" + str(sku.original_price) + ",current_price:" + str(sku.current_price) + \
                        "}"
            redis_connection.hset("cart:common:" + str(customerId), "product_info:" + sku.sku_number, sku_info)

        redis_connection.hset("cart:common:" + str(customerId), 'product_qty:' + skuId, qty)
        return {"message":'{"message": "Success"}', "status":200}
    except:
        return {"message":'{"message": "Failed"}', "status":400}


def deleteCart(customerId, skuId):
    message = deleteCart_Redis(customerId, skuId)
    if message["status"] == 200:
        async_RDBMS.delay(customerId, skuId, 0)
        # async_RDBMS(customerId, skuId, 0)
    return message

def deleteCart_Redis(customerId, skuId):
    message = updateCart_Redis(customerId, skuId, 0)
    return message

def updateCart(customerId, skuId, quantity):
    message = updateCart_Redis(customerId, skuId, quantity)
    if message["status"] == 200:
        async_RDBMS.delay(customerId, skuId, quantity)
        # async_RDBMS(customerId, skuId, quantity)
    return message


def updateCart_Redis(customerId, skuId, quantity):
    quantity = int(quantity)
    if quantity == 0:
        try:
            redis_connection.hdel('cart:common:' + str(customerId), 'product_qty:' + skuId)
            redis_connection.hdel('cart:common:' + str(customerId), 'product_info:' + skuId)
            return {"message":'{"message": "Success"}', "status":200}
        except:
            return {"message": '{"message": "Failed", "}', "status":400}

    try:
        redis_connection.hset('cart:common:' + str(customerId), 'product_qty:' + skuId, quantity)
    except:
        return {"message":'{"message": "Faild"}', "status":400}
    
    return {"message":'{"message": "Success"}', "status":200}

def syncCart_Redis(customerId):
    res = queryCartByCustomerId_RDBMS(customerId)
    for sku in res["skus"]:
        try:
            redis_connection.hset("cart:common:" + str(customerId), "product_qty:" + sku.sku_number, sku.qty)
            sku_info = "{product_number:" + sku.product_number + ",sku_number:" + sku.sku_number + ",name:" + sku.name + \
                       ",main_img:" + sku.main_img + ",original_price:" + str(sku.original_price) + ",current_price:" + str(sku.current_price) + \
                       "}"
            redis_connection.hset("cart:common:" + str(customerId), "product_info:" + sku.sku_number, sku_info)
        except:
            continue

def syncCart_RDBMS(customerId):
    pass


@shared_task
def async_RDBMS(customerId, skuId, quantity):
    quantity = int(quantity)
    skuId = str(skuId)
    logger.info("[app-cart][async-RDBMS][cart:common:" + str(customerId) + ", skuId:" + skuId + "] Asyncing to RDBMS")
    customer = Customer.objects.get(id = customerId)
    try:
        cart = Cart.objects.get(customer = customer)
    except:
        cart = Cart(customer = customer, created_time = timezone.now())
        cart.save()

    try:
        item = CartItem.objects.get(sku_number=skuId)
        if quantity == 0:
            # If it's intended to delete an item from the cart
            item.delete()
        else:
            item.qty = quantity
            item.updated_time = timezone.now()
            item.save()
        logger.info("[app-cart][async-RDBMS][cart:common:" + str(customerId) + ", skuId:" + skuId + "] Asyncing succeed")
    except CartItem.DoesNotExist:
        if quantity > 0:
            item_mongodb = MongoProcessor.query_sku_array_by_sku_number_array([skuId])[0]
            item = CartItem(
                cart=cart, customer=customer, product_number = item_mongodb.product_number,
                sku_number = item_mongodb.sku_number, name = item_mongodb.name,
                main_img = item_mongodb.main_img, original_price = item_mongodb.original_price,
                current_price = item_mongodb.current_price, qty = quantity, created_time = timezone.now(),
                updated_time = timezone.now()
            )
            item.save()
        logger.info("[app-cart][async-RDBMS][cart:common:" + str(customerId) + ", skuId:" + skuId + "] Asyncing succeed")
    
    except Exception as e:
        logger.error("[app-cart][async-RDBMS][cart:common:" + str(customerId) + ", skuId:" + skuId + "] " + str(e))


"""
    Anonymous cart operation
"""

def queryCartBySessionId(sessionId):
    carts_dicc = redis_connection.hgetall("cart:anonymous:" + str(sessionId))
    # Find all the sku number
    carts_skus = list(set([key.split(":")[-1] for key in list(carts_dicc.keys())]))
    # Query the latest information of the sku from MongoDB
    carts_sku_info_list = []

    if len(carts_dicc) > 0:
        carts_info = MongoProcessor.query_sku_array_by_sku_number_array(carts_skus)
        if carts_info != None:
            for sku in carts_info:
                qty = int(carts_dicc["product_qty:" + sku.sku_number])
                newsku = CartItem_DTO(sku, qty)
                carts_sku_info_list.append(newsku)
    else:
        carts_res = {"skus": [], "total": 0}
        return carts_res
        
    total_price = 0

    for sku in carts_sku_info_list:
        qty = sku.qty
        total_price = total_price + sku.current_price * qty
    
    carts_res = {"skus":carts_sku_info_list, "total":total_price}

    return carts_res

def updateCartBySessionId(sessionId, skuId, quantity):
    quantity = int(quantity)
    if quantity == 0:
        try:
            redis_connection.hdel('cart:anonymous:' + str(sessionId), 'product_qty:' + skuId)
            redis_connection.hdel('cart:anonymous:' + str(sessionId), 'product_info:' + skuId)
            return {"message":'{"message": "Success"}', "status":200}
        except:
            return {"message": '{"message": "Failed", "}', "status":400}

    try:
        redis_connection.hset('cart:anonymous:' + str(sessionId), 'product_qty:' + skuId, quantity)
    except:
        return {"message":'{"message": "Faild"}', "status":400}
    
    return {"message":'{"message": "Success"}', "status":200}

def deleteCartBySessionId(sessionId, skuId):
    message = updateCartBySessionId(sessionId, skuId, 0)
    return message

def addCartBySessionId(sessionId, skuId, qty):
    qty = int(qty)
    if_exist = False
    try:
        if redis_connection.exists("cart:anonymous:" + str(sessionId)) > 0:
            if_exist = True

        if redis_connection.hexists("cart:anonymous:" + str(sessionId), "product_qty:" + skuId):
            curr_qty = int(redis_connection.hget("cart:anonymous:" + str(sessionId), "product_qty:" + skuId))
            qty = curr_qty + qty
        else:
            sku = MongoProcessor.query_sku_array_by_sku_number_array([str(skuId)])[0]
            sku_info = "{product_number:" + sku.product_number + ",sku_number:" + sku.sku_number + ",name:" + sku.name + \
                        ",main_img:" + sku.main_img + ",original_price:" + str(sku.original_price) + ",current_price:" + str(sku.current_price) + \
                        "}"
            redis_connection.hset("cart:anonymous:" + str(sessionId), "product_info:" + sku.sku_number, sku_info)

        redis_connection.hset("cart:anonymous:" + str(sessionId), 'product_qty:' + skuId, qty)
        
        # Set expiration time for the anonymous users
        # Test time is 20 seconds
        if not if_exist:
            redis_connection.expire("cart:anonymous:" + str(sessionId), 60*60)

        return {"message":'{"message": "Success"}', "status":200}
    except:
        return {"message":'{"message": "Failed"}', "status":400}

def integrateCart(sessionId, customerId):
    # Check if there is an anonymous cart exist
    if_anonymous = redis_connection.exists("cart:anonymous:" + str(sessionId))
    carts_skus = queryCartByCustomerId(customerId)["skus"]
    if if_anonymous:
        anony_skus = queryCartBySessionId(sessionId)["skus"]
    else:
        anony_skus = []

    sku_item = {}
    for item in carts_skus:
        if item.sku_number in sku_item:
            sku_item[item.sku_number] = sku_item[item.sku_number] + int(item.qty)
        else:
            sku_item[item.sku_number] = int(item.qty)
    
    message = {"message":'{"message": "Success"}', "status":200}

    for item in anony_skus:
        if item.sku_number in sku_item:
            # There is existing cart information of this item about this customer, just update the quantity
            sku_item[item.sku_number] = sku_item[item.sku_number] + int(item.qty)
            message = updateCart(customerId, item.sku_number, sku_item[item.sku_number])
        else:
            # There is no existing item in customer's cart
            sku_item[item.sku_number] = int(item.qty)
            message = addCart(customerId, item.sku_number, int(item.qty))
    
    try:
        redis_connection.delete("cart:anonymous:" + str(sessionId))
    except:
        # The records of the anonymous cart will be deleted automatically after certain time period
        pass

    return message
        
            