from django.shortcuts import render
from apps.customers.views import my_login_required
from apps.carts.views import queryCartByCustomerId_Redis
from apps.customers.models import Customer
from apps.orders.models import Order
from apps.products.services_mongo import MongoProcessor
from config.settings.config_common import \
    LOGTAIL_SOURCE_TOKEN, \
    S3_PRODUCT_IMAGE_THUMBNAIL_URL_PREFIX, \
    S3_PDP_SCREENSHOT_URL_PREFIX, \
    PAGE_SIZE_ORDER_HISTORY
from apps.orders.views import queryOrdersItemsByCustomerId, queryOrdersByCustomerId, order_checkout, order_first_checkout, order_single_checkout, single_order_first_checkout
from logtail import LogtailHandler
import logging

handler = LogtailHandler(source_token=LOGTAIL_SOURCE_TOKEN)
logger = logging.getLogger(__name__)
logger.handlers = []
logger.addHandler(handler)

class OrderPageViews:

    @my_login_required
    def store_orders_checkout_page(request):

        customerId = request.session['Customer'].id
        context = {}
        cur_customer = Customer.objects.get(id = customerId)
        context['FullName'] = cur_customer.first_name + " " + cur_customer.last_name
        # result.first_name + " " + result.last_name
        context['Phone'] = cur_customer.phone
        context['Email'] = cur_customer.email
        context['Shipping'] = cur_customer.shipping_address

        cur_cart = queryCartByCustomerId_Redis(customerId)
        context['total_price'] = cur_cart["total"]

        if not order_first_checkout(customerId):
            return render(request, "online-store/checkout-fail.html")
        else:
            return render(request, "online-store/checkout.html", context)



    @my_login_required
    def store_ajax_orders_history_page(request):
        if request.method == "GET":
            page = request.GET.get("page", 1)
            print(page)

            context = {}
            context['product_img_prefix'] = S3_PRODUCT_IMAGE_THUMBNAIL_URL_PREFIX
            context['pdp_screenshot_prefix'] = S3_PDP_SCREENSHOT_URL_PREFIX
            customerId = request.session['Customer'].id
            context["orderItems"] = queryOrdersItemsByCustomerId(customerId)
            context["orders"] = queryOrdersByCustomerId(customerId, page)

            return render(request, "online-store/segment/product-square-scroll-show-seg.html", context)

    @my_login_required
    def store_orders_history_page(request):
        if request.method == "GET":
            context = {}
            context['product_img_prefix'] = S3_PRODUCT_IMAGE_THUMBNAIL_URL_PREFIX
            context['pdp_screenshot_prefix'] = S3_PDP_SCREENSHOT_URL_PREFIX
            customerId = request.session['Customer'].id
            page = 1
            context["orderItems"] = queryOrdersItemsByCustomerId(customerId)
            context["orders"] = queryOrdersByCustomerId(customerId, page)
            context['page_size'] = PAGE_SIZE_ORDER_HISTORY

            customerId = request.session['Customer'].id
            cur_customer = Customer.objects.get(id=customerId)
            context['total_size'] = Order.objects.filter(customer =cur_customer).count()

            return render(request, "online-store/order.html", context)

    @my_login_required
    def store_orders_pay_page(request):

        if request.method == 'POST':
            if not order_checkout(request):
                return render(request, "online-store/payment-fail.html")
            else:
                return render(request, "online-store/payment-success.html")

    @my_login_required
    def store_orders_single_pay_page(request):
        if request.method == 'POST':
            if not order_single_checkout(request):
                return render(request, "online-store/checkout-fail.html")
            else:
                return render(request, "online-store/payment-success.html")


    @my_login_required
    def store_orders_single_checkout_page(request):
        if request.method == 'POST':
            context = {}
            customerId = request.session['Customer'].id
            cur_customer = Customer.objects.get(id=customerId)
            context['FullName'] = cur_customer.first_name + " " + cur_customer.last_name
            context['Phone'] = cur_customer.phone
            context['Email'] = cur_customer.email
            context['Shipping'] = cur_customer.shipping_address

            sku_number = request.POST.get("sku", None)
            quantity = int(request.POST.get("quantity", None))
            cur_sku_dto = MongoProcessor.query_sku_array_by_sku_number_array([sku_number])
            cur_single_price = cur_sku_dto[0].current_price
            total_price = float(cur_single_price) * float(quantity)
            context['total_price'] = total_price
            context['sku_number'] = sku_number
            context['quantity'] = quantity
            print(sku_number)

            if not single_order_first_checkout(customerId, sku_number, quantity):
                return render(request, "online-store/checkout-fail.html")
            else:
                return render(request, "online-store/single-checkout.html", context)
        #
        # context = {}
        # customerId = request.session['Customer'].id
        # cur_customer = Customer.objects.get(id=customerId)
        # context['FullName'] = cur_customer.first_name + " " + cur_customer.last_name
        # context['Phone'] = cur_customer.phone
        # context['Email'] = cur_customer.email
        # context['Shipping'] = cur_customer.shipping_address
        #
        # sku_number = request.GET.get("sku", None)
        # quantity = int(request.GET.get("quantity", None))
        # cur_sku_dto = MongoProcessor.query_sku_array_by_sku_number_array([sku_number])
        # cur_single_price = cur_sku_dto[0].current_price
        # total_price = float(cur_single_price) * float(quantity)
        # context['total_price'] = total_price
        # context['sku_number'] = sku_number
        # context['quantity'] = quantity
        #
        # if not single_order_first_checkout(customerId):
        #     return render(request, "online-store/checkout-fail.html")
        # else:
        #     return render(request, "online-store/single-checkout.html", context)
        #


        #
        # if not order_single_checkout(request):
        #     return render(request, "online-store/checkout-fail.html")
        # else:
        #     return render(request, "online-store/payment-success.html")
