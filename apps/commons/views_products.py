from django.http.response import Http404, HttpResponseServerError, HttpResponse
from django.shortcuts import render
from apps.orders.models import OrderItem
from apps.products.services_mongo import MongoProcessor
from apps.products.services_neo4j import Neo4jProcessor
from apps.products.services_es import ESProcessor
from apps.catalogs.views import queryCatalogList, queryCatalogById
from apps.customers.views import my_login_required 
from config.settings.config_common import \
    PAGE_SIZE_PRODUCT_LISTING, \
    PAGE_SIZE_PRODUCT_DETAIL_REVIEW, \
    PAGE_SIZE_RECOMMENDED_PRODUCT, \
    LOGTAIL_SOURCE_TOKEN, \
    S3_PRODUCT_IMAGE_FULL_URL_PREFIX, \
    S3_PRODUCT_IMAGE_THUMBNAIL_URL_PREFIX, \
    S3_PDP_SCREENSHOT_URL_PREFIX
from django.core.exceptions import ObjectDoesNotExist
from logtail import LogtailHandler
import logging

handler = LogtailHandler(source_token=LOGTAIL_SOURCE_TOKEN)
logger = logging.getLogger(__name__)
logger.handlers = []
logger.addHandler(handler)


class ProductPageViews:
    def store_products_catalog_page(request):
        if request.method == "GET":
            catalogs = queryCatalogList()
            return render(request, "online-store/catalog.html", {"catalogs": catalogs})

    def store_products_product_list_page(request):
        if request.method == "GET":
            catalog_id = request.GET.get("catalog_id", None)
            search = request.GET.get("search", None)
            brand_array = request.GET.get("brands", None)
            keyword_array = request.GET.get("keywords", None)
            attr_value_array = request.GET.get("attrs", None)
            sattr_value_array = request.GET.get("sattrs", None)
            tag_array = request.GET.get("tags", None)
            feature_value_array = request.GET.get("features", None)
            sort_by = request.GET.get("sort_by", None)
            sort_order = request.GET.get("sort_order", None)
            
            context = {}

            if catalog_id:
                es_filters = ESProcessor.query_filter_array_by_catalog_id_or_search_term(
                    "catalog", catalog_id)
                try:
                    i = int(catalog_id)
                    catalog = queryCatalogById(catalog_id)
                except ObjectDoesNotExist:
                    raise Http404("catalog not found")
                except ValueError:
                    raise Http404("catalog id must be a integer")
                
                context['catalog'] = catalog
            else:
                es_filters = ESProcessor.query_filter_array_by_catalog_id_or_search_term(
                    "search", search)
        
            es_products = ESProcessor.query_product_array_by_multiple_variables(\
                catalog_id, \
                search, \
                brand_array.split(",") if brand_array else None, \
                keyword_array.split(",") if keyword_array else None, \
                attr_value_array.split(",") if attr_value_array else None, \
                sattr_value_array.split(",") if sattr_value_array else None, \
                tag_array.split(",") if tag_array else None, \
                feature_value_array.split(",") if feature_value_array else None, \
                1, \
                PAGE_SIZE_PRODUCT_LISTING, \
                sort_by, \
                sort_order)

            ESProcessor.compare_filter_array_with_product_array_and_add_markers(es_filters, es_products)

            context['es_filters'] = es_filters
            context['es_products'] = es_products
            context['product_img_prefix'] = S3_PRODUCT_IMAGE_THUMBNAIL_URL_PREFIX
            context['product_flag'] = True
            context['scroll_flag'] = False 
            context['tag_show_flag'] = True 
            
            return render(request, "online-store/product-list.html", context)

    def store_products_product_review_list_ajax(request):
        if request.method == "GET":
            product_number = request.GET.get("product_number", None)
            page = request.GET.get("page", 2)
            
            reviewList = MongoProcessor.query_review_array_by_product_number(product_number, page, PAGE_SIZE_PRODUCT_DETAIL_REVIEW)

            return render(request, "online-store/segment/product-detail-review-list-seg.html", {"reviewList": reviewList})
        pass
    
    def store_products_product_list_ajax(request):
        if request.method == "GET":
            catalog_id = request.GET.get("catalog_id", None)
            search = request.GET.get("search", None)
            brand_array = request.GET.get("brands", None)
            keyword_array = request.GET.get("keywords", None)
            attr_value_array = request.GET.get("attrs", None)
            sattr_value_array = request.GET.get("sattrs", None)
            tag_array = request.GET.get("tags", None)
            feature_value_array = request.GET.get("features", None)
            page = request.GET.get("page", 2)
            size = request.GET.get("size", PAGE_SIZE_PRODUCT_LISTING)
            sort_by = request.GET.get("sort_by", None)
            sort_order = request.GET.get("sort_order", None)

            es_products = ESProcessor.query_product_array_by_multiple_variables(catalog_id, search, brand_array.split(",") if brand_array else None, keyword_array.split(",") if keyword_array else None, attr_value_array.split(
                ",") if attr_value_array else None, sattr_value_array.split(",") if sattr_value_array else None, tag_array.split(",") if tag_array else None, feature_value_array.split(",") if feature_value_array else None, page, size, sort_by, sort_order)
            
            context = {}
            context['es_products'] = es_products
            context['product_img_prefix'] = S3_PRODUCT_IMAGE_THUMBNAIL_URL_PREFIX
            context['product_flag'] = True
            context['scroll_flag'] = False 
            context['tag_show_flag'] = True
            
            return render(request, "online-store/segment/product-list-seg.html", context)
    
    def store_products_product_list_for_home_page_ajax(request):
        if request.method == "GET":
            page = request.GET.get("page", 2)
            product_list_sales_rank = ESProcessor.query_product_array_sort_by_sales_for_home_page(page)
            
            context = {}
            context['es_products'] = product_list_sales_rank
            context['product_img_prefix'] = S3_PRODUCT_IMAGE_THUMBNAIL_URL_PREFIX
            context['product_flag'] = True
            context['scroll_flag'] = False 
            context['tag_show_flag'] = False
            
            return render(request, "online-store/segment/product-list-seg.html", context) 

    @my_login_required
    def store_products_add_product_review_ajax(request):
        if request.method == "POST":
            product_number = request.POST.get("product_number", None)
            review_content = request.POST.get("review_content", None)
            review_rating = request.POST.get("review_rating", None)
            
            customer = request.session["Customer"]

            res = MongoProcessor.add_review_by_product_number(
                product_number, review_content, review_rating, customer)

            if res:
                return render(request, "online-store/segment/product-detail-review-seg.html", {"review": res})
            else:
                return HttpResponse("Failed")
        raise Http404()

    def store_products_product_detail_page(request):
        if request.method == "GET":
            product_number = request.GET.get("product_number", None)
            sku_number = request.GET.get("sku", None)

            if product_number:
                product = MongoProcessor.query_product_by_product_number(
                product_number)
            elif sku_number:
                product = MongoProcessor.query_product_by_sku_number(sku_number)
            else:  
                product = None
            
            if not product:
                raise Http404("product not found")
           
            neo4j_product_number_array = Neo4jProcessor.query_recommendation_product_from_neo4j(product_number)
            product_number_array = [] 
            for product_number in neo4j_product_number_array:
                product_number_array.append(product_number)
            recommendation_product_array = ESProcessor.query_product_array_by_product_number_array(True, 1, PAGE_SIZE_RECOMMENDED_PRODUCT, product_number_array)

            context = {}
            context['product'] = product
            context['recommendation_product_array'] = recommendation_product_array
            context['product_img_prefix'] = S3_PRODUCT_IMAGE_THUMBNAIL_URL_PREFIX 
            context['product_flag'] = True
            context['scroll_flag'] = True 
            context['tag_show_flag'] = True 

            return render(request, "online-store/product-detail.html", context)

    @my_login_required
    def store_products_product_snapshot_page(request):
        if request.method == "GET":
            order_item_id = request.GET.get("order_item_id", None)
            if order_item_id:
                try:
                    order_item = OrderItem.objects.get(id=order_item_id)
                except:
                    raise Http404("order item not found")
                
                if order_item.customer.id != request.session["Customer"].id:
                    raise HttpResponseServerError("unauthorized")
                
                filename = order_item.screen_shot
                pdp_screenshot_url = S3_PDP_SCREENSHOT_URL_PREFIX + filename
            
                return render(request, "online-store/product-snapshot.html", 
                    {
                        "pdp_screenshot_url": pdp_screenshot_url,
                        "created_time": order_item.created_time
                    })
            
            raise Http404("order item not found")

        raise Http404() 
   