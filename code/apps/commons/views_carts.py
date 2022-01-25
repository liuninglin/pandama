from django.http.response import HttpResponse
from django.shortcuts import render
from apps.carts.views import queryCartByCustomerId, updateCart, addCart, queryCartBySessionId, updateCartBySessionId, addCartBySessionId
from config.settings.config_common import \
    LOGTAIL_SOURCE_TOKEN, \
    S3_PRODUCT_IMAGE_THUMBNAIL_URL_PREFIX
import logging
logger = logging.getLogger(__name__)

class CartPageViews:
    def store_carts_cart_page(request):
        """
            Tell if the user has logged in or not
            Tell if there is a session key in the request
        """
        #_________________________Tell if the user has logged in first__________________________
        if "Customer" in request.session.keys():
            if_login = True
        else:
            if_login = False

        if not if_login:
            # If not log in
            if not request.session.session_key:
                request.session.create()
                # Set expiration time 60 minutes | for test set 5 minutes
                request.session.set_expiry(60 * 60)
            # Get the session id for later operation
            sessionId = request.session.session_key
            
            # Test integrating anonymous records and existing records
            # integrateCart(sessionId, 2)

            # Test putting the user object in the session
            # customer = Customer.objects.get(id=1)
            # request.session["Customer"] = customer
            
            if request.method == "GET":
                carts_res = queryCartBySessionId(sessionId)
                return render(request, "online-store/cart.html", 
                            {"cart": carts_res["skus"], "total_price":carts_res["total"], "product_img_prefix": S3_PRODUCT_IMAGE_THUMBNAIL_URL_PREFIX})

        else:
            # If log in
            if request.method == "GET":
                customerId = request.session["Customer"].id
                carts_res = queryCartByCustomerId(customerId)
                return render(request, "online-store/cart.html", 
                            {"cart": carts_res["skus"], "total_price":carts_res["total"], "product_img_prefix": S3_PRODUCT_IMAGE_THUMBNAIL_URL_PREFIX})
    
    def store_carts_cart_update(request):
        #_________________________Tell if the user has logged in first__________________________
        if "Customer" in request.session.keys():
            if_login = True
        else:
            if_login = False

        if not if_login:
            # If not log in
            if not request.session.session_key:
                request.session.create()
                # Set expiration time 60 minutes | for test set 5 minutes
                request.session.set_expiry(60 * 60)
            # Get the session id for later operation
            sessionId = request.session.session_key

            if request.method == "POST":
                sku_number = request.POST.get("sku_number")
                qty = request.POST.get("latest_qty")
                
                res = updateCartBySessionId(sessionId, sku_number, qty)
                return  HttpResponse(res["message"], content_type='application/json', status=res["status"])
        else:
            if request.method == "POST":
                sku_number = request.POST.get("sku_number")
                customerId = request.session["Customer"].id # need to be changed later
                qty = request.POST.get("latest_qty")
                
                res = updateCart(customerId, sku_number, qty)
                return  HttpResponse(res["message"], content_type='application/json', status=res["status"])

    def store_carts_cart_add(request):
        #_________________________Tell if the user has logged in first__________________________
        if "Customer" in request.session.keys():
            if_login = True
        else:
            if_login = False

        if not if_login:
            # If not log in
            if not request.session.session_key:
                request.session.create()
                # Set expiration time 60 minutes | for test set 5 minutes
                request.session.set_expiry(60 * 60)
            # Get the session id for later operation
            sessionId = request.session.session_key
            if request.method == "POST":
                sku_number = request.POST.get("sku_number")
                qty = request.POST.get("quantity")
                res = addCartBySessionId(sessionId, sku_number, qty)
                return HttpResponse(res["message"], content_type='application/json', status=res["status"])
        else:
            if request.method == "POST":
                sku_number = request.POST.get("sku_number")
                customerId = request.session["Customer"].id
                qty = request.POST.get("quantity")
                res = addCart(customerId, sku_number, qty)
                return HttpResponse(res["message"], content_type='application/json', status=res["status"])
      