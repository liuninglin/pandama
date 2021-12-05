from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from apps.products.services_es import ESProcessor
from apps.customers.views import my_login_required, queryCustomersByCustomerId, deleteProductInWishlist, addProductToWishilist
from apps.carts.views import integrateCart
from apps.customers.models import Customer, Wishlist
from config.settings.config_common import \
    PAGE_SIZE_WISHLIST_LISTING, \
    LOGTAIL_SOURCE_TOKEN, \
    S3_PRODUCT_IMAGE_THUMBNAIL_URL_PREFIX
import hashlib
from django.core.exceptions import ObjectDoesNotExist
import re
import os
import random
import math
from django.utils import timezone
from logtail import LogtailHandler
import logging

handler = LogtailHandler(source_token=LOGTAIL_SOURCE_TOKEN)
logger = logging.getLogger(__name__)
logger.handlers = []
logger.addHandler(handler)

class CustomerPageViews:
    
    def store_customers_register(request):
        if "Customer" in request.session.keys():
            product_list_new = ESProcessor.query_product_array_tag_new_for_home_page()
            product_list_sales_rank = ESProcessor.query_product_array_sort_by_sales_for_home_page(1)
            
            context = {}
            context['product_list_new'] = product_list_new
            context['product_list_sales_rank'] = product_list_sales_rank
            context['product_img_prefix'] = S3_PRODUCT_IMAGE_THUMBNAIL_URL_PREFIX
            return render(request, "online-store/home.html", context)
        else:
            if request.method == "GET":
                return render(request, "online-store/register.html")
            else:
                username = request.POST["username"]
                email = request.POST["email"]
                password = request.POST["password"]
                confirm_password = request.POST["confirm_password"]
                context = {}
                try: 
                    Customer.objects.get(username=username)
                    context["feedback"] = "Username exists"
                    return render(request, "online-store/register.html", context)
                except:
                    findCustomer = None
                
                if password == None or password == "":
                    context["feedback"] = "Invalid password"
                    return render(request, "online-store/register.html", context)

                if password != confirm_password:
                    context["feedback"] = "Unmatched passwords"
                    return render(request, "online-store/register.html", context)
                
                if email == None:
                    context["feedback"] = "Invalid email"
                    return render(request, "online-store/register.html", context)

                if not re.findall(".*@.+\..*", email):
                    context["feedback"] = "Invalid email address"
                    return render(request, "online-store/register.html", context)
                
                salt = ""
                for i in range(6):
                    index = math.floor(random.random() * 10)
                    salt += str(index)

                hash_value = hashlib.sha256((salt + password).encode()).hexdigest()
                customer = Customer(username=username, email=email, last_login_time=timezone.now(),
                                    password=hash_value, pass_salt=salt, created_time=timezone.now(),
                                    updated_time=timezone.now())
                customer.save()
                context["feedback"] = "Success Registration"
                return redirect("store_customers_login_page")

    @my_login_required
    def store_customers_logout(request):
        if request.method == "GET":
            del request.session["Customer"]
            
            return redirect("store_customers_home_page")

    def store_customers_home_page(request):
        if request.method == "GET":
            product_list_new = ESProcessor.query_product_array_tag_new_for_home_page()
            product_list_sales_rank = ESProcessor.query_product_array_sort_by_sales_for_home_page(1)
            
            context = {}
            context['product_list_new'] = product_list_new
            context['product_list_sales_rank'] = product_list_sales_rank
            context['product_img_prefix'] = S3_PRODUCT_IMAGE_THUMBNAIL_URL_PREFIX
            context['tagsection_product_flag'] = True
            context['tagsection_scroll_flag'] = True 
            context['tagsection_tag_show_flag'] = False
            context['bestsellersection_product_flag'] = True
            context['bestsellersection_scroll_flag'] = False
            context['bestsellersection_tag_show_flag'] = False
            
            return render(request, "online-store/home.html", context)

    def store_customers_login_page(request):
        if request.method == "GET":
            if "Customer" in request.session.keys():
                product_list_new = ESProcessor.query_product_array_tag_new_for_home_page()
                product_list_sales_rank = ESProcessor.query_product_array_sort_by_sales_for_home_page(1)
                
                context = {}
                context['product_list_new'] = product_list_new
                context['product_list_sales_rank'] = product_list_sales_rank
                context['product_img_prefix'] = S3_PRODUCT_IMAGE_THUMBNAIL_URL_PREFIX
                return redirect('store_customers_home_page')
                # return render(request, "online-store/home.html", context)
                
            return render(request, "online-store/login.html")

        username = request.POST['username']
        password = request.POST['password']
        try: 
            customer = Customer.objects.get(username = username)
        except ObjectDoesNotExist:
            customer = None
        if customer is None:
            return render(request, "online-store/login.html", {"feedback" : "Please check your username and password!"})
        savedPassword = customer.password
        salt = customer.pass_salt
        hash = hashlib.sha256((salt + password).encode()).hexdigest()

        if hash == savedPassword:
            if request.session.session_key:
                integrateCart(request.session.session_key, customer.id)

            request.session['Customer'] = customer
            product_list_new = ESProcessor.query_product_array_tag_new_for_home_page()
            product_list_sales_rank = ESProcessor.query_product_array_sort_by_sales_for_home_page(1)
            
            context = {}
            context['product_list_new'] = product_list_new
            context['product_list_sales_rank'] = product_list_sales_rank
            context['product_img_prefix'] = S3_PRODUCT_IMAGE_THUMBNAIL_URL_PREFIX

 
            last_path = request.META.get('HTTP_REFERER')
            if "next" not in last_path:
                return redirect("store_customers_home_page")  
            last_path = last_path[(last_path.index("next=") + 5):]
            if last_path != "":
                return redirect(last_path)
            else:
                return redirect("store_customers_home_page") 
        
        return render(request, "online-store/login.html", {"feedback" : "Please check your username and password!"})

    @my_login_required
    def store_customers_profile_show_page(request):
        if 'Customer' not in request.session.keys():
            return render(request, "online-store/login.html")
        customerId = request.session['Customer'].id
        result = queryCustomersByCustomerId(customerId)
        context = {}
        context['Username'] = result.username
        # result.username
        context['FullName'] = result.first_name + " " + result.last_name
        # result.first_name + " " + result.last_name
        context['Phone'] = result.phone
        context['Email'] = result.email
        context['Shipping'] = result.shipping_address
        context['product_img_prefix'] = S3_PRODUCT_IMAGE_THUMBNAIL_URL_PREFIX

        return render(request, "online-store/profile.html", context)
    
    @my_login_required
    def store_customers_profile_edit_img(request):
        """
            Process the request to update the image of the customer
        """
        if request.method == "POST":
            result = request.session["Customer"]
            context = {}
            context['Username'] = result.username
            context['FullName'] = result.first_name + " " + result.last_name
            context['Phone'] = result.phone
            context['Email'] = result.email
            context['Shipping'] = result.shipping_address
            context['product_img_prefix'] = S3_PRODUCT_IMAGE_THUMBNAIL_URL_PREFIX

            img = request.FILES["img"]
            if not img or not hasattr(img, "content_type"):
                context["feedback"] = "You must upload a picture"
                return render(request, "online-store/edit-profile.html", context)
            if not img.content_type or not img.content_type.startswith("image"):
                context["feedback"] = "File type is not image"
                return render(request, "online-store/edit-profile.html", context)
            if img.size > 2500000:
                context["feedback"] = "File too big (max size is {0} bytes)".format(2500000)
                return render(request, "online-store/edit-profile.html", context)
           
            if result.img.name is not None and result.img.name != "":
                prev_img = result.img.path
                if prev_img.startswith("online-store/img/core-img"):
                    pass
                else:
                    if os.path.exists(prev_img):
                        os.remove(prev_img)

            result.img = img
            
            try:
                result.save()
            except:
                context["feedback"] = "Uploading failed"
                return render(request, "online-store/edit-profile.html", context)

            request.session["Customer"] = result

            return render(request, "online-store/edit-profile.html", context)
            

    @my_login_required
    def store_customers_profile_edit_page(request):
        if request.method == "GET":
            customerId = request.session['Customer'].id

            result = queryCustomersByCustomerId(customerId)
            context = {}
            context['Username'] = result.username
            # result.username
            context['FullName'] = result.first_name + " " + result.last_name
            # result.first_name + " " + result.last_name
            context['Phone'] = result.phone
            context['Email'] = result.email
            context['Shipping'] = result.shipping_address
            context['product_img_prefix'] = S3_PRODUCT_IMAGE_THUMBNAIL_URL_PREFIX
            return render(request, "online-store/edit-profile.html", context)
        # request.user.username = Profile(username = request.POST['username'])

        customerId = request.session['Customer'].id
        result = queryCustomersByCustomerId(customerId)
        # ----------------------------------------------
        context = {}
        context['Username'] = request.POST['username']
        context['FullName'] = request.POST['realname']
        # result.first_name + " " + result.last_name
        context['Phone'] = request.POST['phone']
        context['Email'] = request.POST['email']
        context['Shipping'] = request.POST['address']
        context['product_img_prefix'] = S3_PRODUCT_IMAGE_THUMBNAIL_URL_PREFIX
        #-----------------------------------------------
        if request.POST["username"] == "":
            context["feedback"] = "Username invalid"
            return render(request, "online-store/edit-profile.html", context)
        result.username = request.POST['username']

        words = [word for word in request.POST['realname'].split(" ") if word != ""]

        if len(words) == 0:
            context["feedback"] = "Invalid Full Name"
            return render(request, "online-store/edit-profile.html", context)
        if len(words) >= 1:
            result.first_name = words[0]
        if len(words) >= 2:
            result.last_name = words[1]
        else:
            result.last_name = ""
        
        phone = re.findall("([(]?[\d]{3}[)]?[-][\d]{3}[-][\d]{4})|([(]?[\d]{3}[)]?[-]?[\d]{3}[-]?[\d]{4})", request.POST["phone"])
        if not phone:
            context["feedback"] = "Invalid phone number format"
            return render(request, "online-store/edit-profile.html", context)
        result.phone = request.POST['phone']

        email = re.findall(".*@.+\..*", request.POST["email"])
        if not email:
            context["feedback"] = "Invalid email address"
            return render(request, "online-store/edit-profile.html", context)
        result.email = request.POST['email']

        result.shipping_address = request.POST['address']
        result.save()
        context["feedback"] = "Success"

        # Update the customer into the session
        request.session["Customer"] = result

        return render(request, "online-store/profile.html", context)

    @my_login_required
    def store_customers_wish_list_ajax(request):
        if request.method == "GET":
            page = request.GET.get("page", 1)
            cur_customer = request.session["Customer"]
            wish_lists = cur_customer.wishlists
            product_number_list = []

            fromIndex = (int(page) - 1) * PAGE_SIZE_WISHLIST_LISTING
            toIndex = fromIndex + PAGE_SIZE_WISHLIST_LISTING

            for item in wish_lists.all().order_by('-created_time')[fromIndex : toIndex]:
                product_number_list.append(item.product_number)
            if len(product_number_list) > 0:
                es_products = ESProcessor.query_product_array_by_product_number_array(False, page, PAGE_SIZE_WISHLIST_LISTING ,product_number_list)
            else:
                es_products = []
            
            context = {}
            context['es_products'] = es_products
            context['product_img_prefix'] = S3_PRODUCT_IMAGE_THUMBNAIL_URL_PREFIX
            context['product_flag'] = False
            context['scroll_flag'] = False 
            context['tag_show_flag'] = True 
             
            return render(request, "online-store/segment/product-list-seg.html", context)


    @my_login_required
    def store_customers_wish_list(request):
        if request.method == "GET":
            customerId = request.session['Customer'].id
            cur_customer = Customer.objects.get(id = customerId)
            wish_lists = cur_customer.wishlists
            product_number_list = []
            total_size = len(wish_lists.all())

            fromIndex = 0
            toIndex = PAGE_SIZE_WISHLIST_LISTING

            es_products = []
            for item in wish_lists.all().order_by('-created_time')[fromIndex: toIndex]:
                for item in wish_lists.all():
                    product_number_list.append(item.product_number)

                if len(product_number_list) > 0:
                    es_products = ESProcessor.query_product_array_by_product_number_array(False, 1, PAGE_SIZE_WISHLIST_LISTING ,product_number_list)
                else:
                    es_products = []
                
            context = {}
            context['es_products'] = es_products
            context['page_size'] = PAGE_SIZE_WISHLIST_LISTING 
            context['total_size'] = total_size
            context['product_img_prefix'] = S3_PRODUCT_IMAGE_THUMBNAIL_URL_PREFIX
            context['product_flag'] = False
            context['scroll_flag'] = False
            context['tag_show_flag'] = True
                    
            return render(request, "online-store/wishlist-list.html", context)


    @my_login_required
    def store_customers_add_to_wish_list(request):
        if request.method == "GET":
            customerId = request.session['Customer'].id
            product_number = request.GET.get("product_number")
            res = addProductToWishilist(product_number, customerId)
            return HttpResponse(res["message"], content_type='application/json', status=res["status"])

    @my_login_required
    def store_customers_delete_wish_list(request):
        if request.method == "POST":
            customerId = request.session['Customer'].id
            product_number = request.POST.get("product_number")

            res = deleteProductInWishlist(product_number, customerId)
            return HttpResponse(res["message"], content_type='application/json', status=res["status"])

