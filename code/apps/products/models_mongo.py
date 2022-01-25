from mongoengine import Document, EmbeddedDocument
from mongoengine.fields import DateTimeField, DecimalField, EmbeddedDocumentField, StringField, IntField, ListField
from mongoengine.connection import connect
from config.settings.config_mongo import MONGODB_URL

connect(host=MONGODB_URL)

class MongoAttrModel(EmbeddedDocument):
    name = StringField(max_length=100, required=True)
    value = StringField(max_length=100, required=True)

class MongoSkuModel(EmbeddedDocument):
    sku_number = StringField(max_length=100, required=True)
    sku_img_array = ListField(StringField())
    attr_array = ListField(EmbeddedDocumentField(MongoAttrModel))
    sattr_array = ListField(EmbeddedDocumentField(MongoAttrModel)) 

class MongoCustomerModel(EmbeddedDocument):
    id = StringField(max_length=50, required=True)
    first_name = StringField(max_length=200, required=True)
    last_name = StringField(max_length=200, required=True)
    profile_img = StringField()

class MongoReviewModel(EmbeddedDocument):
    customer = EmbeddedDocumentField(MongoCustomerModel) 
    content = StringField(max_length=500, required=True)
    created_time = DateTimeField(required=True)
    star = IntField(required=True)

class MongoProductModel(Document):
    product_number = StringField(max_length=100, required=True)
    name = StringField(max_length=200, required=True) 
    chinese_name = StringField(max_length=200, required=True)
    brand = StringField(max_length=100, required=True)
    catalog_id_array = ListField(StringField(max_length=50, required=True))
    main_img = StringField()
    other_img_array = ListField(StringField())
    publish_status = IntField(required=True)
    original_price = DecimalField(precision=2, decimal_places=2, max_digits=10)
    current_price = DecimalField(precision=2, decimal_places=2, max_digits=10)
    stock = IntField(required=True)
    safe_stock = IntField(required=True)
    description = StringField()
    keyword_array = ListField(StringField(max_length=100))
    created_time = DateTimeField(required=True)
    updated_time = DateTimeField(required=True)
    created_user_id = StringField(max_length=50, required=True)
    updated_user_id = StringField(max_length=50, required=True)
    avg_star = DecimalField(precision=2, decimal_places=2, max_digits=10) 
    review_array = ListField(EmbeddedDocumentField(MongoReviewModel))
    sku_array = ListField(EmbeddedDocumentField(MongoSkuModel))
    tag_array = ListField(StringField(max_length=100))
    feature_array = ListField(EmbeddedDocumentField(MongoAttrModel))
    changed_flag = IntField(required=True)
    sales = IntField(required=True)
    sales_rank = IntField(required=True)
    source = StringField(max_length=100)
    version = StringField(max_length=100)
    type = StringField(max_length=100)

    meta = {'collection': 'products'}