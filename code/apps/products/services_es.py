from apps.products.services_mongo import MongoProcessor
from apps.products.services_neo4j import Neo4jProcessor
from apps.products.models_es import ESProductModel
from apps.products.models_dto import ESProduct2DTO
from apps.commons.tools import CommonTools
from config.settings.config_es import ES_URL, ES_INDEX_PRODUCTS
from config.settings.config_common import \
    LOGTAIL_SOURCE_TOKEN, \
    DYNAMIC_SYS_SETTINGS_LOCKER_INDEX_ASYNC_PROCESS, \
    PAGE_SIZE_HOME_PAGE_NEW_SECTION, \
    PAGE_SIZE_HOME_PAGE_TOP_SALE_SECTION
from elasticsearch.client import Elasticsearch
import jsonpickle
from celery import shared_task

import logging
logger = logging.getLogger(__name__)

es = Elasticsearch(hosts=[ES_URL])

class ESProcessor:
    def common_query(query_body):
        res = es.search(index=ES_INDEX_PRODUCTS, body=query_body)
        for hit in res["hits"]["hits"]:
            hit["source"] = hit["_source"]
            del hit["_source"]
        return res

    def query_filter_array_by_catalog_id_or_search_term(page, catalog_id_or_search_term):
        query_body = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"publish_status": 1}},
                    ]
                }
            },
            "aggs": {
                "brand_terms": {
                    "terms": {
                        "field": "brand"
                    }
                },
                "cataglog_id_array_terms": {
                    "terms": {
                        "field": "catalog_id_array.keyword"
                    }
                },
                "keyword_array_terms": {
                    "terms": {
                        "field": "keyword_array.keyword"
                    }
                },
                "sku_number_array_terms": {
                    "terms": {
                        "field": "sku_number_array.keyword"
                    }
                },
                "attr_array_terms": {
                    "nested": {
                        "path": "attr_array"
                    },
                    "aggs": {
                        "attr_name_terms": {
                            "terms": {
                                "field": "attr_array.name.keyword"
                            },
                            "aggs": {
                                "attr_values_terms": {
                                    "terms": {
                                        "field": "attr_array.value.keyword"
                                    }
                                }
                            }
                        }
                    }
                },
                "sattr_array_terms": {
                    "nested": {
                        "path": "sattr_array"
                    },
                    "aggs": {
                        "sattr_name_terms": {
                            "terms": {
                                "field": "sattr_array.name.keyword"
                            },
                            "aggs": {
                                "sattr_values_terms": {
                                    "terms": {
                                        "field": "sattr_array.value.keyword"
                                    }
                                }
                            }
                        }
                    }
                },
                "tag_array_terms": {
                    "terms": {
                        "field": "tag_array.keyword"
                    }
                },
                "feature_array_terms": {
                    "nested": {
                        "path": "feature_array"
                    },
                    "aggs": {
                        "feature_name_terms": {
                            "terms": {
                                "field": "feature_array.name.keyword"
                            },
                            "aggs": {
                                "feature_values_terms": {
                                    "terms": {
                                        "field": "feature_array.value.keyword"
                                    }
                                }
                            }
                        }
                    }
                },
                "sales_terms": {
                    "terms": {
                        "field": "sales"
                    }
                },
                "sales_rank_terms": {
                    "terms": {
                        "field": "sales_rank"
                    }
                }
            }
        }

        if catalog_id_or_search_term is not None and catalog_id_or_search_term != "":
            if page == "catalog":
                query_body["query"]["bool"]["must"].append(
                    {"match": {"catalog_id_array": catalog_id_or_search_term}})
            elif page == "search":
                query_body["query"]["bool"]["must"].append({"multi_match": {
                    "query":    catalog_id_or_search_term,
                    "fields": ["product_number", "name", "sku_number_array", "chinese_name"]
                }})

        return ESProcessor.common_query(query_body)
    
    '''
    Query products by parameters from es
    Return a list of products and filtering properties

    the relationship between parameters is AND

    catalog_id: searching products by catalog_id
    search_term: searching products by name, product_number, sku
    brand: searching products by brand
    attrs_value_array: an array of values of attributes(determine the sku) to filter, the relationship of values is OR
    sattrs_value_array: an array of values of attributes(not determine the sku) to filter, the relationship of values is OR
    page: page number, from 1 to n
    size: page size, from 1 to n
    '''
    def query_product_array_by_multiple_variables(catalog_id, search_term, brands_array, keywords_array, attrs_value_array, sattrs_value_array, tag_array, feature_value_array, page, page_size, sort_by, sort_order):
        query_body = {
                "sort" : [
                    
                ],
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"publish_status": 1}},
                        ]
                    }
                },
                "aggs": {
                    "brand_terms": {
                        "terms": {
                            "field": "brand"
                        }
                    },
                    "cataglog_id_array_terms": {
                        "terms": {
                            "field": "catalog_id_array.keyword"
                        }
                    },
                    "keyword_array_terms": {
                        "terms": {
                            "field": "keyword_array.keyword"
                        }
                    },
                    "sku_number_array_terms": {
                        "terms": {
                            "field": "skus.keyword"
                        }
                    },
                    "attr_array_terms": {
                        "nested": {
                            "path": "attr_array"
                        },
                        "aggs": {
                            "attr_name_terms": {
                                "terms": {
                                    "field": "attr_array.name.keyword"
                                },
                                "aggs": {
                                    "attr_values_terms": {
                                        "terms": {
                                            "field": "attr_array.value.keyword"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "sattr_array_terms": {
                        "nested": {
                            "path": "sattr_array"
                        },
                        "aggs": {
                            "sattr_name_terms": {
                                "terms": {
                                    "field": "sattr_array.name.keyword"
                                },
                                "aggs": {
                                    "sattr_values_terms": {
                                        "terms": {
                                            "field": "sattr_array.value.keyword"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "tag_array_terms": {
                        "terms": {
                            "field": "tag_array.keyword"
                        }
                    },
                    "feature_array_terms": {
                        "nested": {
                            "path": "feature_array"
                        },
                        "aggs": {
                            "feature_name_terms": {
                                "terms": {
                                    "field": "feature_array.name.keyword"
                                },
                                "aggs": {
                                    "feature_values_terms": {
                                        "terms": {
                                            "field": "feature_array.value.keyword"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "sales_terms": {
                        "terms": {
                            "field": "sales"
                        }
                    },
                    "sales_rank_terms": {
                        "terms": {
                            "field": "sales_rank"
                        }
                    }
                },
                "size": int(page_size),
                "from": ((int(page) - 1) * int(page_size))
            }    

        if search_term is not None and search_term != "":
            query_body["query"]["bool"]["must"].append({"multi_match": {
                "query":    search_term,
                "fields": ["product_number", "name", "sku_number_array", "chinese_name"]
            }})

        if catalog_id is not None and catalog_id != "":
            query_body["query"]["bool"]["must"].append(
                {"match": {"catalog_id_array": catalog_id}})

        if brands_array is not None:
            tmp = {
                "bool": {
                    "should": [

                    ]
                }
            }
            for brand in brands_array:
                tmp["bool"]["should"].append({"match": {"brand": brand}})
            query_body["query"]["bool"]["must"].append(tmp)

        if keywords_array is not None:
            tmp = {
                "bool": {
                    "should": [

                    ]
                }
            }
            for keyword in keywords_array:
                tmp["bool"]["should"].append(
                    {"match": {"keyword_array.keyword": keyword}})
            query_body["query"]["bool"]["must"].append(tmp)

        if attrs_value_array is not None:
            temp = {
                "nested": {
                    "path": "attr_array",
                    "query": {
                        "bool": {
                            "should": [

                            ]
                        }
                    }
                }
            }
            for attr_value in attrs_value_array:
                temp["nested"]["query"]["bool"]["should"].append(
                    {"match": {"attr_array.value.keyword": attr_value}})
            query_body["query"]["bool"]["must"].append(temp)

        if sattrs_value_array is not None:
            temp = {
                "nested": {
                    "path": "sattr_array",
                            "query": {
                                "bool": {
                                    "should": [

                                    ]
                                }
                            }
                }
            }
            for sattr_value in sattrs_value_array:
                temp["nested"]["query"]["bool"]["should"].append(
                    {"match": {"sattr_array.value.keyword": sattr_value}})
            query_body["query"]["bool"]["must"].append(temp)

        if tag_array is not None:
            tmp = {
                "bool": {
                    "should": [

                    ]
                }
            }
            for tag in tag_array:
                tmp["bool"]["should"].append(
                    {"match": {"tag_array.keyword": tag}})
            query_body["query"]["bool"]["must"].append(tmp)

        if feature_value_array is not None:
            temp = {
                "nested": {
                    "path": "feature_array",
                            "query": {
                                "bool": {
                                    "should": [

                                    ]
                                }
                            }
                }
            }
            for feature_value in feature_value_array:
                temp["nested"]["query"]["bool"]["should"].append(
                    {"match": {"feature_array.value.keyword": feature_value}})
            query_body["query"]["bool"]["must"].append(temp)

        if sort_by is not None and sort_order is not None:
            query_body["sort"].append({sort_by: sort_order})
        else:
            query_body["sort"].append({"sales": "desc"}) 
        
        return ESProcessor.common_query(query_body)

    def compare_filter_array_with_product_array_and_add_markers(es_filters, es_products):
        es_products_str = str(es_products)

        for brand in es_filters["aggregations"]["brand_terms"]["buckets"]:
            if ('\'key\': \'' + brand["key"] + '\'') not in es_products_str:
                brand["show"] = False
            else:
                brand["show"] = True
        for keyword in es_filters["aggregations"]["keyword_array_terms"]["buckets"]:
            if ('\'key\': \'' + keyword["key"] + '\'') not in es_products_str:
                keyword["show"] = False
            else:
                keyword["show"] = True 
        for attr in es_filters["aggregations"]["attr_array_terms"]["attr_name_terms"]["buckets"]:
            for attr_value in attr["attr_values_terms"]["buckets"]:
                if ('\'key\': \'' + attr_value["key"] + '\'') not in es_products_str:
                    attr_value["show"] = False
                else:
                    attr_value["show"] = True 
        for sattr in es_filters["aggregations"]["sattr_array_terms"]["sattr_name_terms"]["buckets"]:
            for sattr_value in sattr["sattr_values_terms"]["buckets"]:
                if ('\'key\': \'' + sattr_value["key"] + '\'') not in es_products_str:
                    sattr_value["show"] = False
                else:
                    sattr_value["show"] = True 
        for tag in es_filters["aggregations"]["tag_array_terms"]["buckets"]:
            if ('\'key\': \'' + tag["key"] + '\'') not in es_products_str:
                tag["show"] = False
            else:
                tag["show"] = True 
        for feature in es_filters["aggregations"]["feature_array_terms"]["feature_name_terms"]["buckets"]:
            for feature_value in feature["feature_values_terms"]["buckets"]:
                if ('\'key\': \'' + feature_value["key"] + '\'') not in es_products_str:
                    feature_value["show"] = False
                else:
                    feature_value["show"] = True 

    def add_index_from_mongo():
        product_number_array_changed = MongoProcessor.query_changed_product_number_array()
        if len(product_number_array_changed) <= 0 or len(product_number_array_changed[0]["sync_product_number_array"]) <= 0:
            return None

        product_array = MongoProcessor.query_product_array_by_product_number_array(
            product_number_array_changed[0]["sync_product_number_array"])

        res_array = []
        for product in product_array:
            es.delete_by_query(index=ES_INDEX_PRODUCTS, body={"query": {"match": {"product_number": product["product_number"]}}})
            res = es.index(index=ES_INDEX_PRODUCTS, body=jsonpickle.encode(ESProduct2DTO(product), unpicklable=False))
            res_array.append(res)

            Neo4jProcessor.sync_product_into_neo4j(product)
        MongoProcessor.update_product_changed_flag_by_product_number_array(
            product_number_array_changed[0]["sync_product_number_array"])
        
        return res_array

    def create_mapping():
        try:
            es.indices.delete(index=ES_INDEX_PRODUCTS, ignore=[400, 404])
        except Exception:
            pass

        try:
            res = es.indices.create(index=ES_INDEX_PRODUCTS,
                                    ignore=400, body=ESProductModel.products_mapping)
            return res
        except Exception:
            return "complete"

    def delete_all_index():
        try:
            es.delete_by_query(index=ES_INDEX_PRODUCTS, body={"query": {"match_all": {}}})
        except Exception:
            pass
        
        logger.info("deleted all index")
    
    def query_product_array_and_sort_and_pagination(random_flag, query_json, sort_by, sort_order, page, page_size):
        query_body = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "match": {
                                    "publish_status": "1"
                                }
                            }
                        ]
                    }
                },
                "size": int(page_size),
                "from": int(page) - 1
            }
        
        if not random_flag: 
            if sort_by:
                query_body["sort"] = [
                    {
                        sort_by: sort_order
                        } 
                    ]
            else:
                query_body["sort"] = [
                        {
                            "sales": "desc"
                            } 
                        ] 
        
        if random_flag:
            query_body["query"]["bool"]["must"].append(
                {
                    "function_score": {
                        "random_score": {
                        }
                    }
                }
            )
            
        if query_json:
            query_body["query"]["bool"]["must"].append(query_json)
        
        return ESProcessor.common_query(query_body)
    
    def query_product_array_tag_new_for_home_page():
        query_json = {
                "match": {
                    "tag_array.keyword": "中国"
                }
            }
        return ESProcessor.query_product_array_and_sort_and_pagination(True, query_json, None, None, 1, PAGE_SIZE_HOME_PAGE_NEW_SECTION) 
    
    def query_product_array_sort_by_sales_for_home_page(page):
        query_json = {
                "match": {
                    "tag_array.keyword": "bestseller"
                }
            }
        return ESProcessor.query_product_array_and_sort_and_pagination(True, query_json, None, None, page, PAGE_SIZE_HOME_PAGE_TOP_SALE_SECTION)                         

    def query_product_array_by_product_number_array(random_flag, page, page_size, product_number_array):
        
        tmp = {
                "bool": {
                    "should": [

                    ]
                }
            }
        for product_number in product_number_array:
            tmp["bool"]["should"].append({"match": {"product_number": product_number}})
        
        return ESProcessor.query_product_array_and_sort_and_pagination(random_flag, tmp, None, None, page, page_size)                         

    @shared_task
    def async_es_index():
        logger.info("[app-products][async-index] es index creating started")
        CommonTools.update_settings_by_key(DYNAMIC_SYS_SETTINGS_LOCKER_INDEX_ASYNC_PROCESS, "1")
        
        try:
            ESProcessor.add_index_from_mongo()
            logger.info("[app-products][async-index] es index completed")   
        except Exception as e:
            logger.error("[app-products][async-index] es index creating occurred error: " + str(e))
            
        CommonTools.update_settings_by_key(DYNAMIC_SYS_SETTINGS_LOCKER_INDEX_ASYNC_PROCESS, "0")
  