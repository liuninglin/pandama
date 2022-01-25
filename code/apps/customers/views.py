from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render, reverse
from apps.customers.models import Customer, Wishlist
from django.utils import timezone
from django.db import transaction

# Hard code now
# Replace the hardcode id with 1
def queryCustomersByCustomerId(customerId):
    # TODO: Customer Domain - Query customers by customerId from Relational Database
    # Return Object Customer ojb in models.py
    customer = Customer.objects.get(id=customerId)

    return customer


# Do we need the request param?
def updateCustomerByCustomerId(request, customerId, customer):
    # TODO: Customer Domain - Update customer by customerId from Relational Database
    # If successful return True, else return False
    return True


# refer https://code.activestate.com/recipes/498217-custom-django-login_required-decorator/
# Decorator to check the login status
def my_login_required(f):
    def wrap(request, *args, **kwargs):
            #this check the session if userid key exist, if not it will redirect to login page
        if "ajax" in request.path:
            if 'Customer' not in request.session.keys():
                return HttpResponse(status=401)
        else:
            if 'Customer' not in request.session.keys():
                return redirect(reverse('store_customers_login_page') + "?next=" + request.path)
        return f(request, *args, **kwargs)
    wrap.__doc__=f.__doc__
    wrap.__name__=f.__name__
    return wrap



@transaction.atomic
def addProductToWishilist(product_number, customerId):
    # a customer can have many wishlist

    cur_customer = Customer.objects.get(id=customerId)
    wishlist_array = cur_customer.wishlists
    for cur_wishlist in wishlist_array.all():
        if product_number == cur_wishlist.product_number:
            return {"message": '{"message": "Success"}', "status": 200}

    try:
        cur_customer = Customer.objects.get(id=customerId)
        cur_wishlists = cur_customer.wishlists

        new_wishlist = Wishlist.objects.create(
            customer=cur_customer,
            product_number=product_number,
            created_time=timezone.now()
        )
    except:
        return {"message":'{"message": "Failed"}', "status":400}

    return {"message": '{"message": "Success"}', "status": 200}

@transaction.atomic
def deleteProductInWishlist(cur_product_number, customerId):

    cur_customer = Customer.objects.get(id=customerId)

    try:
        Wishlist.objects.filter(customer = cur_customer, product_number=cur_product_number).delete()
    except:
        return {"message":'{"message": "Failed"}', "status":400}

    return {"message": '{"message": "Success"}', "status": 200}



# def queryWishLists():
#     cur_curstomer = Customer.objects.get(id=1)
#
#     wish_lists = cur_customer.wishlists
#     product_number_list = []
#     for item in wish_lists:
#         product_number_list.append(item.product_number)
#     return ES_Processor.es_queryProductListByProductNumberList(page, product_number_list)
#