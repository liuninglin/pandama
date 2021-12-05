class ESProductModel:
  products_mapping = \
  {
    "settings":{
        "number_of_shards":1,
        "number_of_replicas":0
    },
    "mappings":{
        "properties":{
          "product_number":{
              "type":"text"
          },
          "name":{
              "type":"text"
          },
          "chinese_name":{
              "type":"text"
          },
          "brand":{
              "type":"keyword"
          },
          "catalog_id_array":{
              "type":"text",
              "fields":{
                "keyword":{
                    "type":"keyword",
                    "ignore_above":256
                }
              }
          },
          "main_img":{
              "type":"text"
          },
          "other_img_array":{
              "type":"text",
              "fields":{
                "keyword":{
                    "type":"keyword",
                    "ignore_above":256
                }
              }
          },
          "publish_status":{
              "type":"integer"
          },
          "original_price":{
              "type":"double"
          },
          "current_price":{
              "type":"double"
          },
          "stock":{
              "type":"integer"
          },
          "safe_stock":{
              "type":"integer"
          },
          "description":{
              "type":"text"
          },
          "keyword_array":{
              "type":"text",
              "fields":{
                "keyword":{
                    "type":"keyword",
                    "ignore_above":256
                }
              }
          },
          "created_time":{
              "type":"date"
          },
          "updated_time":{
              "type":"date"
          },
          "created_user_id":{
              "type":"long"
          },
          "updated_user_id":{
              "type":"long"
          },
          "avg_star":{
              "type":"double"
          },
          "sku_number_array":{
              "type":"text",
              "fields":{
                "keyword":{
                    "type":"keyword",
                    "ignore_above":256
                }
              }
          },
          "attr_array":{
              "type":"nested",
              "properties":{
                "name":{
                    "type":"text",
                    "fields":{
                      "keyword":{
                          "type":"keyword",
                          "ignore_above":256
                      }
                    }
                },
                "value":{
                    "type":"text",
                    "fields":{
                      "keyword":{
                          "type":"keyword",
                          "ignore_above":256
                      }
                    }
                }
              }
          },
          "sattr_array":{
              "type":"nested",
              "properties":{
                "name":{
                    "type":"text",
                    "fields":{
                      "keyword":{
                          "type":"keyword",
                          "ignore_above":256
                      }
                    }
                },
                "value":{
                    "type":"text",
                    "fields":{
                      "keyword":{
                          "type":"keyword",
                          "ignore_above":256
                      }
                    }
                }
              }
          },
          "tag_array":{
              "type":"text",
              "fields":{
                "keyword":{
                    "type":"keyword",
                    "ignore_above":256
                }
              }
          },
          "feature_array":{
              "type":"nested",
              "properties":{
                "name":{
                    "type":"text",
                    "fields":{
                      "keyword":{
                          "type":"keyword",
                          "ignore_above":256
                      }
                    }
                },
                "value":{
                    "type":"text",
                    "fields":{
                      "keyword":{
                          "type":"keyword",
                          "ignore_above":256
                      }
                    }
                }
              }
          },
          "sales":{
              "type":"integer"
          },
          "sales_rank":{
              "type":"integer"
          },
          "source":{
              "type":"text"
          },
          "type":{
              "type":"text"
          }
        }
    }
  }


