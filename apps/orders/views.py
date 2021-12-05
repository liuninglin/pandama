from django.shortcuts import render
from apps.customers.models import Customer
from apps.carts.models import *
from apps.orders.models import *
from django.utils import timezone
from django.db import transaction
from apps.carts.views import queryCartByCustomerId_Redis, deleteCart
from apps.products.services_mongo import MongoProcessor
from decimal import *
from apps.products.services_screenshot import ScreenshotProcessor
from celery import shared_task
import jsonpickle
from config.settings.config_common import LOGTAIL_SOURCE_TOKEN
from logtail import LogtailHandler
from config.settings.config_common import PAGE_SIZE_ORDER_HISTORY
import logging

handler = LogtailHandler(source_token=LOGTAIL_SOURCE_TOKEN)
logger = logging.getLogger(__name__)
logger.handlers = []
logger.addHandler(handler)


@transaction.atomic
def order_checkout_precheck_customer(total_price, customerId):

    cur_customer = Customer.objects.get(id=customerId)
    cur_balance = cur_customer.balance

    if cur_balance <= total_price:
        return False

    return True


@transaction.atomic
def order_checkout_precheck_stockcheck(cartItem_dto_list):
    for single_item_dto in cartItem_dto_list:
        cur_sku_dto = MongoProcessor.query_sku_array_by_sku_number_array([single_item_dto.sku_number])
        cur_safe_stock = cur_sku_dto[0].safe_stock
        cur_amount = single_item_dto.qty
        cur_stock = cur_sku_dto[0].stock

        if cur_stock - cur_amount < cur_safe_stock:
            return False

    return True


@transaction.atomic
def order_checkout_precheck(cartItem_dto_list, total_price, customerId):
    flag_customer = order_checkout_precheck_customer(total_price, customerId)

    flag_stock = order_checkout_precheck_stockcheck(cartItem_dto_list)
    if flag_customer and flag_stock:
        print("TRUE")
        return True
    else:
        print("FALSE")
        return False



def order_first_checkout(customerId):

    cur_cart = queryCartByCustomerId_Redis(customerId)
    total_price = cur_cart["total"]
    cartItem_dto_list = cur_cart["skus"]

    if not order_checkout_precheck(cartItem_dto_list, total_price, customerId):
        return False
    else:
        return True


def single_order_first_checkout(customerId, sku_number, quantity):
    # sku_number = request.POST.get("sku_number", None)
    # quantity = int(request.POST.get("quantity", None))

    cur_customer = Customer.objects.get(id=customerId)
    cur_sku_dto = MongoProcessor.query_sku_array_by_sku_number_array([sku_number])
    cur_stock = cur_sku_dto[0].stock
    cur_safe_stock = cur_sku_dto[0].safe_stock
    cur_single_price = cur_sku_dto[0].current_price
    total_price = float(cur_single_price) * float(quantity)

    if cur_stock - quantity < cur_safe_stock:
        print("-----cur_stock - quantity < cur_safe_stock")
        return False

    if cur_customer.balance < total_price:
        print("cur_customer.balance < total_price")
        return False

    return True

@transaction.atomic
def order_checkout(request):
    save_id = transaction.savepoint()
    customerId = request.session['Customer'].id
    cur_customer = Customer.objects.get(id=customerId)

    cur_cart = queryCartByCustomerId_Redis(customerId)
    total_price = cur_cart["total"]
    cartItem_dto_list = cur_cart["skus"]


    new_email = request.POST.get('Email', cur_customer.email);

    new_phone = request.POST.get('Phone',  cur_customer.phone);
    new_shipping = request.POST.get('Shipping', cur_customer.shipping_address);


    if order_checkout_precheck(cartItem_dto_list, total_price, customerId):

        new_order = Order.objects.create(customer=cur_customer,
                                         created_time=timezone.now(),
                                         customer_firstname=cur_customer.first_name,
                                         customer_lastname=cur_customer.last_name,
                                         customer_phone= new_phone,
                                         customer_email=new_email,
                                         customer_shipping_address=new_shipping,
                                         total_price=total_price,
                                         status=0)

        for item in cartItem_dto_list:

            cur_product_sku = item.sku_number
            # check lastest price from product_sku instead of item
            product_sku_dto = MongoProcessor.query_sku_array_by_sku_number_array([cur_product_sku])



            # // screenshot xxxxx
            # //version= product_sku_dto.version


            new_order_item = OrderItem.objects.create(
                order = new_order,
                customer = cur_customer,
                # product = product_sku_dto[0],
                product_number = item.product_number,
                product_sku = cur_product_sku,
                product_name = item.name,
                product_img = item.main_img,
                product_original_price = item.original_price,
                product_current_price = item.current_price,
                amount=item.qty,
                created_time=timezone.now(),
                status = 0,
                version= product_sku_dto[0].version,
                redundant_product_info_json=jsonpickle.encode(product_sku_dto,  unpicklable=False),
                screen_shot=str(new_order.id) + '_' + str(item.product_number) + ".png" 
            )
            
            create_screenshots.delay(new_order.id, item.product_number)

            flag = deleteCart(customerId, item.sku_number)



            print(cur_customer.balance)

        cur_customer.balance = cur_customer.balance - Decimal.from_float(total_price)
        cur_customer.save()
        print(cur_customer.balance)
        request.session["Customer"] = Customer.objects.get(id=customerId)

        transaction.savepoint_commit(save_id)
        return True
    else:
        transaction.savepoint_rollback(save_id)
        return False


@shared_task
def create_screenshots(order_id, product_number):
    ScreenshotProcessor.pdp_screenshot(order_id, product_number)
    logger.info("[screenshot] created screent shot for order: " + str(order_id) + " product_number: " + str(product_number))


def queryOrdersItemsByCustomerId(customerId):

    cur_customer = Customer.objects.get(id=customerId)
    if not cur_customer:
        return []

    orderItem_list = OrderItem.objects.filter(customer=cur_customer).order_by("-created_time")
    return orderItem_list


def queryOrdersByCustomerId(customerId, page):

    cur_customer = Customer.objects.get(id=customerId)
    if not cur_customer:
        return []
    fromIndex = (int(page) - 1) * PAGE_SIZE_ORDER_HISTORY
    endIndex = fromIndex + PAGE_SIZE_ORDER_HISTORY
    order_list = Order.objects.filter(customer=cur_customer).order_by("-created_time")[fromIndex : endIndex]
    return order_list


@transaction.atomic
def order_single_checkout(request):

    sku_number = request.POST.get("sku_number", None)
    quantity = int(request.POST.get("quantity", None))

    customerId = request.session['Customer'].id
    cur_customer = Customer.objects.get(id=customerId)
    new_email = request.POST.get('Email', cur_customer.email);
    new_phone = request.POST.get('Phone',  cur_customer.phone);
    new_shipping = request.POST.get('Shipping', cur_customer.shipping_address);

    cur_sku_dto = MongoProcessor.query_sku_array_by_sku_number_array([sku_number])
    cur_stock = cur_sku_dto[0].stock
    cur_safe_stock = cur_sku_dto[0].safe_stock
    cur_single_price = cur_sku_dto[0].current_price
    total_price = float(cur_single_price) *  float(quantity)

    if cur_stock - quantity < cur_safe_stock:
        return False

    if cur_customer.balance < total_price:
        return False


    save_id = transaction.savepoint()
    new_order = Order.objects.create(customer=cur_customer,
                                     created_time=timezone.now(),
                                     customer_firstname=cur_customer.first_name,
                                     customer_lastname=cur_customer.last_name,
                                     customer_phone=new_phone,
                                     customer_email=new_email,
                                     customer_shipping_address=new_shipping,
                                     total_price=total_price,
                                     status=0)

    new_order_item = OrderItem.objects.create(
                order = new_order,
                customer = cur_customer,
                # product = product_sku_dto[0],
                product_number = cur_sku_dto[0].product_number,
                product_sku = cur_sku_dto[0].sku_number,
                product_name = cur_sku_dto[0].name,
                product_img = cur_sku_dto[0].main_img,
                product_original_price = cur_sku_dto[0].original_price,
                product_current_price = cur_sku_dto[0].current_price,
                amount=quantity,
                created_time=timezone.now(),
                status = 0,
                version= cur_sku_dto[0].version,
                redundant_product_info_json=jsonpickle.encode(cur_sku_dto[0],  unpicklable=False),
                screen_shot=str(new_order.id) + '_' + str(cur_sku_dto[0].product_number) + ".png"
            )

    create_screenshots.delay(new_order.id, cur_sku_dto[0].product_number)

    cur_customer.balance = cur_customer.balance - Decimal.from_float(total_price)
    cur_customer.save()
    request.session["Customer"] = Customer.objects.get(id=customerId)
    transaction.savepoint_commit(save_id)
    return True



