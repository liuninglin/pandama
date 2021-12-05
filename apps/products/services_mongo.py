from apps.products.models_mongo import MongoCustomerModel, MongoProductModel, MongoReviewModel
from apps.products.models_dto import MongoProduct2DTO
from config.settings.config_common import LOGTAIL_SOURCE_TOKEN, PAGE_SIZE_PRODUCT_DETAIL_REVIEW
import datetime
from logtail import LogtailHandler
import logging

handler = LogtailHandler(source_token=LOGTAIL_SOURCE_TOKEN)
logger = logging.getLogger(__name__)
logger.handlers = []
logger.addHandler(handler)

class MongoProcessor:
    def common_query_body():
        return [
            {
                "$project":{
                    "product_number":1,
                    "name":1,
                    "chinese_name":1,
                    "brand":1,
                    "catalog_id_array":1,
                    "main_img":1,
                    "other_img_array":1,
                    "publish_status":1,
                    "original_price":1,
                    "current_price":1,
                    "stock":1,
                    "safe_stock":1,
                    "description":1,
                    "keyword_array":1,
                    "created_time":1,
                    "updated_time":1,
                    "created_user_id":1,
                    "updated_user_id":1,
                    "avg_star":1,
                    "review_array":{
                        "$reverseArray":"$review_array"
                    },
                    "sku_array":1,
                    "tag_array":1,
                    "feature_array":1,
                    "sales":1,
                    "sales_rank":1,
                    "source":1,
                    "type":1,
                    "version":1,
                    "sku_array_tmp":"$sku_array"
                }
            },
            {
                "$unwind":"$sku_array_tmp"
            },
            {
                "$replaceRoot":{
                    "newRoot":{
                        "$mergeObjects":[
                        {
                            "product_number":"$product_number",
                            "name":"$name",
                            "chinese_name":"$chinese_name",
                            "brand":"$brand",
                            "catalog_id_array":"$catalog_id_array",
                            "main_img":"$main_img",
                            "other_img_array":"$other_img_array",
                            "publish_status":"$publish_status",
                            "original_price":"$original_price",
                            "current_price":"$current_price",
                            "stock":"$stock",
                            "safe_stock":"$safe_stock",
                            "description":"$description",
                            "keyword_array":"$keyword_array",
                            "created_time":"$created_time",
                            "updated_time":"$updated_time",
                            "created_user_id":"$created_user_id",
                            "updated_user_id":"$updated_user_id",
                            "avg_star":"$avg_star",
                            "review_array":{
                                "$slice":[
                                    "$review_array",
                                    PAGE_SIZE_PRODUCT_DETAIL_REVIEW
                                ]
                            },
                            "sku_array":"$sku_array",
                            "tag_array":"$tag_array",
                            "feature_array":"$feature_array",
                            "sales":"$sales",
                            "sales_rank":"$sales_rank",
                            "source":"$source",
                            "version":"$version",
                            "type":"$type"
                        },
                        "$sku_array_tmp"
                        ]
                    }
                }
            },
            {
                "$unwind":{
                    "path":"$attr_array",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$group":{
                    "_id":{
                        "attr_name":"$attr_array.name",
                        "attr_value":"$attr_array.value",
                        "product_number":"$product_number",
                        "name":"$name",
                        "chinese_name":"$chinese_name",
                        "brand":"$brand",
                        "catalog_id_array":"$catalog_id_array",
                        "main_img":"$main_img",
                        "other_img_array":"$other_img_array",
                        "publish_status":"$publish_status",
                        "original_price":"$original_price",
                        "current_price":"$current_price",
                        "stock":"$stock",
                        "safe_stock":"$safe_stock",
                        "description":"$description",
                        "keyword_array":"$keyword_array",
                        "created_time":"$created_time",
                        "updated_time":"$updated_time",
                        "created_user_id":"$created_user_id",
                        "updated_user_id":"$updated_user_id",
                        "avg_star":"$avg_star",
                        "review_array":"$review_array",
                        "sku_array":"$sku_array",
                        "tag_array":"$tag_array",
                        "feature_array":"$feature_array",
                        "sales":"$sales",
                        "sales_rank":"$sales_rank",
                        "source":"$source",
                        "version":"$version",
                        "type":"$type"
                    },
                    "attr_value_array":{
                        "$addToSet":{
                        "sku_number":"$sku_number",
                        "attr_name":"$attr_array.name",
                        "attr_value":"$attr_array.value"
                        }
                    }
                }
            },
            {
                "$group":{
                    "_id":{
                        "attr_name":"$_id.attr_name",
                        "product_number":"$_id.product_number",
                        "name":"$_id.name",
                        "chinese_name":"$_id.chinese_name",
                        "brand":"$_id.brand",
                        "catalog_id_array":"$_id.catalog_id_array",
                        "main_img":"$_id.main_img",
                        "other_img_array":"$_id.other_img_array",
                        "publish_status":"$_id.publish_status",
                        "original_price":"$_id.original_price",
                        "current_price":"$_id.current_price",
                        "stock":"$_id.stock",
                        "safe_stock":"$_id.safe_stock",
                        "description":"$_id.description",
                        "keyword_array":"$_id.keyword_array",
                        "created_time":"$_id.created_time",
                        "updated_time":"$_id.updated_time",
                        "created_user_id":"$_id.created_user_id",
                        "updated_user_id":"$_id.updated_user_id",
                        "avg_star":"$_id.avg_star",
                        "review_array":"$_id.review_array",
                        "sku_array":"$_id.sku_array",
                        "tag_array":"$_id.tag_array",
                        "feature_array":"$_id.feature_array",
                        "sales":"$_id.sales",
                        "sales_rank":"$_id.sales_rank",
                        "source":"$_id.source",
                        "version":"$_id.version",
                        "type":"$_id.type"
                    },
                    "attr_value_array":{
                        "$addToSet":{
                        "sku_number_array":"$attr_value_array.sku_number",
                        "attr_name":"$_id.attr_name",
                        "attr_value":"$_id.attr_value"
                        }
                    }
                }
            },
            {
                "$group":{
                    "_id":{
                        "product_number":"$_id.product_number",
                        "name":"$_id.name",
                        "chinese_name":"$_id.chinese_name",
                        "brand":"$_id.brand",
                        "catalog_id_array":"$_id.catalog_id_array",
                        "main_img":"$_id.main_img",
                        "other_img_array":"$_id.other_img_array",
                        "publish_status":"$_id.publish_status",
                        "original_price":"$_id.original_price",
                        "current_price":"$_id.current_price",
                        "stock":"$_id.stock",
                        "safe_stock":"$_id.safe_stock",
                        "description":"$_id.description",
                        "keyword_array":"$_id.keyword_array",
                        "created_time":"$_id.created_time",
                        "updated_time":"$_id.updated_time",
                        "created_user_id":"$_id.created_user_id",
                        "updated_user_id":"$_id.updated_user_id",
                        "avg_star":"$_id.avg_star",
                        "review_array":"$_id.review_array",
                        "sku_array":"$_id.sku_array",
                        "tag_array":"$_id.tag_array",
                        "feature_array":"$_id.feature_array",
                        "sales":"$_id.sales",
                        "sales_rank":"$_id.sales_rank",
                        "source":"$_id.source",
                        "version":"$_id.version",
                        "type":"$_id.type"
                    },
                    "attr_array_pdp":{
                        "$push":{
                        "attr_name":"$_id.attr_name",
                        "attr_value_array":"$attr_value_array"
                        }
                    }
                }
            },
            {
                "$project":{
                    "_id":0,
                    "product_number":"$_id.product_number",
                    "name":"$_id.name",
                    "chinese_name":"$_id.chinese_name",
                    "brand":"$_id.brand",
                    "catalog_id_array":"$_id.catalog_id_array",
                    "main_img":"$_id.main_img",
                    "other_img_array":"$_id.other_img_array",
                    "publish_status":"$_id.publish_status",
                    "original_price":"$_id.original_price",
                    "current_price":"$_id.current_price",
                    "stock":"$_id.stock",
                    "safe_stock":"$_id.safe_stock",
                    "description":"$_id.description",
                    "keyword_array":"$_id.keyword_array",
                    "created_time":"$_id.created_time",
                    "updated_time":"$_id.updated_time",
                    "created_user_id":"$_id.created_user_id",
                    "updated_user_id":"$_id.updated_user_id",
                    "avg_star":"$_id.avg_star",
                    "review_array":"$_id.review_array",
                    "sku_array":"$_id.sku_array",
                    "tag_array":"$_id.tag_array",
                    "feature_array":"$_id.feature_array",
                    "attr_array_pdp":"$attr_array_pdp",
                    "sales":"$_id.sales",
                    "sales_rank":"$_id.sales_rank",
                    "source":"$_id.source",
                    "version":"$_id.version",
                    "type":"$_id.type"
                }
            }
            ]
    
    def query_product_by_product_number(product_number):
        aggregate_array = [
                {
                    "$match": {
                        "product_number": product_number
                    }
                }
            ]    
        aggregate_array.extend(MongoProcessor.common_query_body())  
        product_array = list(MongoProductModel.objects().aggregate(aggregate_array))

        if len(product_array) == 0:
            return None
        else:
            return product_array[0]

    def query_product_by_sku_number(sku_number):
        aggregate_array = [
                {
                    "$match": {
                        "sku_array.sku_number": sku_number
                    }
                }
            ]    
        aggregate_array.extend(MongoProcessor.common_query_body())  
        product_array = list(MongoProductModel.objects().aggregate(aggregate_array))

        if len(product_array) == 0:
            return None
        else:
            return product_array[0]

    def query_review_array_by_product_number(product_number, page_number, page_size):
        query_body = [
            {
                "$match":{
                    "product_number": str(product_number)
                }
            },
            {
                "$project":{
                    "review":{
                        "$reverseArray":"$review_array"
                    }
                }
            },
            {
                "$unwind":"$review"
            },
            {
                "$skip":(int(page_number) - 1) * int(page_size)
            },
            {
                "$limit":int(page_size)
            },
            {
                "$project":{
                    "customer":"$review.customer",
                    "content":"$review.content",
                    "created_time":"$review.created_time",
                    "star":"$review.star"
                }
            }
            ]
        review_array = list(MongoProductModel.objects().aggregate(query_body))

        if len(review_array) == 0:
            return None
        else:
            return review_array

    def query_sku_array_by_sku_number_array(sku_number_array):
        query_body = [
                {
                    "$match": {
                        "sku_array.sku_number": {
                            "$in": sku_number_array
                        }
                    }
                },
                {
                    "$unwind": "$sku_array"
                },
                {
                    "$match": {
                        "sku_array.sku_number": {
                            "$in": sku_number_array
                        }
                    }
                },
                {
                    "$replaceRoot": {
                        "newRoot": {
                            "$mergeObjects": [
                                {
                                    "_id": "$_id",
                                    "product_number": "$product_number",
                                    "name": "$name",
                                    "chinese_name": "$chinese_name",
                                    "brand": "$brand",
                                    "catalog_id_array": "$catalog_id_array",
                                    "main_img": "$main_img",
                                    "other_img_array": "$other_img_array",
                                    "publish_status": "$publish_status",
                                    "original_price": "$original_price",
                                    "current_price": "$current_price",
                                    "stock": "$stock",
                                    "safe_stock": "$safe_stock",
                                    "description": "$description",
                                    "keyword_array": "$keyword_array",
                                    "created_time": "$created_time",
                                    "updated_time": "$updated_time",
                                    "created_user_id": "$created_user_id",
                                    "updated_user_id": "$updated_user_id",
                                    "avg_star": "$avg_star",
                                    "tag_array": "$tag_array",
                                    "feature_array": "$feature_array",
                                    "sales": "$sales",
                                    "sales_rank": "$sales_rank",
                                    "source": "$source",
                                    "version": "$version",
                                    "type": "$type"
                                },
                                "$sku_array"
                            ]
                        }
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "product_number": "$product_number",
                        "name": "$name",
                        "chinese_name": "$chinese_name",
                        "brand": "$brand",
                        "catalog_id_array": "$catalog_id_array",
                        "main_img": "$main_img",
                        "other_img_array": "$other_img_array",
                        "publish_status": "$publish_status",
                        "original_price": "$original_price",
                        "current_price": "$current_price",
                        "stock": "$stock",
                        "safe_stock": "$safe_stock",
                        "description": "$description",
                        "keyword_array": "$keyword_array",
                        "created_time": "$created_time",
                        "updated_time": "$updated_time",
                        "created_user_id": "$created_user_id",
                        "updated_user_id": "$updated_user_id",
                        "avg_star": "$avg_star",
                        "sku_number": "$sku_number",
                        "sku_img_array": "$sku_img_array",
                        "attr_array": "$attr_array",
                        "sattr_array": "$sattr_array",
                        "tag_array": "$tag_array",
                        "feature_array": "$feature_array",
                        "sales": "$sales",
                        "sales_rank": "$sales_rank",
                        "source": "$source",
                        "version": "$version",
                        "type": "$type"
                    }
                }
            ]
        product_array = list(MongoProductModel.objects().aggregate(query_body))

        res = []
        for product in product_array:
            res.append(MongoProduct2DTO(product))
            
        return res

    def query_changed_product_number_array():
        query_body = [
                {
                    "$match": {
                        "changed_flag": 1
                    }
                },
                {
                    "$group": {
                        "_id": "null",
                        "sync_product_number_array": {
                            "$addToSet": "$product_number"
                        }
                    }
                }
            ]
        productNumberArray = list(MongoProductModel.objects().aggregate(query_body))
        return productNumberArray

    def query_product_array_by_product_number_array(product_number_array):
        if len(product_number_array) == 0:
            return None

        query_body = [
                {
                    "$match": {
                        "product_number": {
                            "$in": product_number_array
                        }
                    }
                },
                {
                    "$unwind": "$sku_array"
                },
                {
                    "$replaceRoot": {
                        "newRoot": {
                            "$mergeObjects": [
                                {
                                    "product_number": "$product_number",
                                    "name": "$name",
                                    "chinese_name": "$chinese_name",
                                    "brand": "$brand",
                                    "catalog_id_array": "$catalog_id_array",
                                    "main_img": "$main_img",
                                    "other_img_array": "$other_img_array",
                                    "publish_status": "$publish_status",
                                    "original_price": "$original_price",
                                    "current_price": "$current_price",
                                    "stock": "$stock",
                                    "safe_stock": "$safe_stock",
                                    "description": "$description",
                                    "keyword_array": "$keyword_array",
                                    "created_time": "$created_time",
                                    "updated_time": "$updated_time",
                                    "created_user_id": "$created_user_id",
                                    "updated_user_id": "$updated_user_id",
                                    "avg_star": "$avg_star",
                                    "tag_array": "$tag_array",
                                    "feature_array": "$feature_array",
                                    "sales": "$sales",
                                    "sales_rank": "$sales_rank",
                                    "source": "$source",
                                    "version": "$version",
                                    "type": "$type"
                                },
                                "$sku_array"
                            ]
                        }
                    }
                },
                {
                    "$unwind": {
                        "path": "$attr_array",
                        "preserveNullAndEmptyArrays": True
                    }
                },
                {
                    "$unwind": {
                        "path": "$sattr_array",
                        "preserveNullAndEmptyArrays": True
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "product_number": "$product_number",
                            "name": "$name",
                            "chinese_name": "$chinese_name",
                            "brand": "$brand",
                            "catalog_id_array": "$catalog_id_array",
                            "main_img": "$main_img",
                            "other_img_array": "$other_img_array",
                            "publish_status": "$publish_status",
                            "original_price": "$original_price",
                            "current_price": "$current_price",
                            "stock": "$stock",
                            "safe_stock": "$safe_stock",
                            "description": "$description",
                            "keyword_array": "$keyword_array",
                            "created_time": "$created_time",
                            "updated_time": "$updated_time",
                            "created_user_id": "$created_user_id",
                            "updated_user_id": "$updated_user_id",
                            "avg_star": "$avg_star",
                            "tag_array": "$tag_array",
                            "feature_array": "$feature_array",
                            "sales": "$sales",
                            "sales_rank": "$sales_rank",
                            "source": "$source",
                            "version": "$version",
                            "type": "$type"
                        },
                        "attr_array": {
                            "$addToSet": "$attr_array"
                        },
                        "sattr_array": {
                            "$addToSet": "$sattr_array"
                        },
                        "sku_number_array": {
                            "$addToSet": "$sku_number"
                        }
                    }
                },
                {
                    "$project": {
                        "product_number": "$_id.product_number",
                        "name": "$_id.name",
                        "chinese_name": "$_id.chinese_name",
                        "brand": "$_id.brand",
                        "catalog_id_array": "$_id.catalog_id_array",
                        "main_img": "$_id.main_img",
                        "other_img_array": "$_id.other_img_array",
                        "publish_status": "$_id.publish_status",
                        "original_price": "$_id.original_price",
                        "current_price": "$_id.current_price",
                        "stock": "$_id.stock",
                        "safe_stock": "$_id.safe_stock",
                        "description": "$_id.description",
                        "keyword_array": "$_id.keyword_array",
                        "created_time": "$_id.created_time",
                        "updated_time": "$_id.updated_time",
                        "created_user_id": "$_id.created_user_id",
                        "updated_user_id": "$_id.updated_user_id",
                        "avg_star": "$_id.avg_star",
                        "sku_number_array": "$sku_number_array",
                        "attr_array": "$attr_array",
                        "sattr_array": "$sattr_array",
                        "tag_array": "$_id.tag_array",
                        "feature_array": "$_id.feature_array",
                        "sales": "$_id.sales",
                        "sales_rank": "$_id.sales_rank",
                        "source": "$_id.source",
                        "version": "$_id.version",
                        "type": "$_id.type"
                    }
                }
            ] 
        product_array = list(MongoProductModel.objects().aggregate(query_body))

        return product_array

    def add_review_by_product_number(product_number, content, star, customer):
        product = MongoProductModel.objects(product_number=product_number)
        
        if product.count() == 0:
            return None
        else:
            product = product[0]

            review = MongoReviewModel(
                content=content,
                star=star,
                created_time=datetime.datetime.now(),
                customer=MongoCustomerModel(
                    id=str(customer.id),
                    first_name=customer.first_name,
                    last_name=customer.last_name,
                    profile_img=customer.img.name))
            product.review_array.append(review)
            product.avg_star = (float(product.avg_star * len(product.review_array)
                                      ) + float(star)) / (len(product.review_array) + 1)
            product.changed_flag = 1
            product.save()
            return review

    def update_product_changed_flag_by_product_number_array(product_number_array):
        if len(product_number_array) == 0:
            return False

        MongoProductModel.objects(product_number__in=product_number_array).update(changed_flag=0)
        
        return True

    def delete_all_products():
        MongoProductModel.objects().delete()
        logger.info("deleted all mongo data")
