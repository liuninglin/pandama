class CartItem_DTO:
    meta = [
        "product_number",
        "name",
        "chinese_name",
        "brand",
        "catalog_id_array",
        "main_img",
        "other_img_array",
        "publish_status",
        "original_price",
        "current_price", 
        "stock",
        "safe_stock",
        "description",
        "keyword_array",
        "created_time",
        "updated_time",
        "created_user_id",
        "updated_user_id",
        "avg_star",
        "sku_number",
        "sku_img_array",
        "attr_array",
        "sattr_array",
        "tag_array",
        "feature_array",
        "sales",
        "sales_rank",
        "source",
        "type"
    ]
    def __init__(self, dbitem, qty) -> None:
        dict = dbitem.__dict__
        for key in dict:
            if key in dict:
                setattr(self, key, dict[key])
        setattr(self, "qty", qty)