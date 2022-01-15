from neo4j import GraphDatabase
from config.settings.config_neo4j import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from config.settings.config_common import LOGTAIL_SOURCE_TOKEN, PAGE_SIZE_RECOMMENDED_PRODUCT
from apps.orders.models import Order, OrderItem
import logging
from celery import shared_task

logger = logging.getLogger(__name__)

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

class Neo4jProcessor:
    def sync_product_into_neo4j(product):
        with driver.session() as session:
            session.run("""
                    MATCH (o:Order)-[orders:ORDERS]->(p:Product)
                    WHERE p.product_number = toString($product_number)
                    DELETE orders
                """, product_number = str(product['product_number']))
            
            session.run("""
                    MATCH (p:Product) 
                    WHERE p.product_number = $product_number 
                    DELETE p
                """, product_number=product['product_number'])
            
            session.run("""
                CREATE (p:Product {
                    product_number: $product_number,
                    name: $name,
                    chinese_name: $chinese_name,
                    catalog_id_array: $catalog_id_array,
                    brand: $brand,
                    original_price: toFloat($original_price),
                    current_price: toFloat($current_price),
                    avg_star: toFloat($avg_star),
                    sales: toInteger($sales),
                    sales_rank: toInteger($sales_rank),
                    keyword_array: $keyword_array,
                    tag_array: $tag_array,
                    source: $source,
                    version: $version,
                    type: $type
                })
            """, 
            product_number = product['product_number'],
            name = product['name'],
            chinese_name = product['chinese_name'],
            catalog_id_array = product['catalog_id_array'],
            brand = product['brand'],
            original_price = str(product['original_price']),
            current_price = str(product['current_price']),
            avg_star = str(product['avg_star']),
            sales = str(product['sales']),
            sales_rank = str(product['sales_rank']),
            keyword_array = product['keyword_array'],
            tag_array = product['tag_array'],
            source = product['source'],
            version = product['version'],
            type = product['type'])
    
    @shared_task
    def sync_order_from_db():
        try:
            order_array = Order.objects.filter(sync_flag=False)
        except Order.DoesNotExist:
            return
        
        order_id_array = [order.id for order in order_array] 
        for order in order_array:
            with driver.session() as session:
                session.run("""
                    MATCH (o:Order)-[orders:ORDERS]->(p:Product)
                    WHERE o.id = toString($order_id)
                    DELETE orders
                """,
                order_id = str(order.id))
                
                session.run("""
                    MATCH (o:Order)
                    WHERE o.id = toString($order_id)
                    DELETE o
                """,
                order_id = str(order.id)) 
                
                session.run("""
                    CREATE (o:Order {
                        id: $id,
                        customer_id: $customer_id,
                        total_price: toFloat($total_price),
                        created_time: datetime($created_time)
                    })
                """, 
                id = str(order.id),
                customer_id = str(order.customer.id),
                total_price = str(order.total_price),
                created_time = order.created_time)
                
            try:
                order_item_array = order.orderitems.all()
            except OrderItem.DoesNotExist:
                continue
            
            for order_item in order_item_array:                
                session.run("""
                    MATCH (p:Product), (o:Order)
                    WHERE p.product_number = $product_number AND o.id = $order_id
                    CREATE (o)-[orders:ORDERS{
                        quantity: toInteger($amount)
                    }]->(p)
                """,
                product_number = str(order_item.product_number),
                order_id = str(order.id),
                amount = order_item.amount)
            
            order.sync_flag = True
            order.save()
        
        return order_id_array
            
    def query_recommendation_product_from_neo4j(product_number):
        with driver.session() as session:
            result = session.run("""
                MATCH (p1:Product{product_number:$product_number})<-[:ORDERS]-(:Order)-[:ORDERS]->(p2:Product{catalog_id_array:p1.catalog_id_array}) 
                WHERE p2.product_number <> p1.product_number 
                RETURN p2.product_number as product_number, count(*) as purchaseCount
                ORDER BY purchaseCount DESC 
                LIMIT $page_size
            """,
            product_number = str(product_number),
            page_size = PAGE_SIZE_RECOMMENDED_PRODUCT)
            
            return [record["product_number"] for record in result]
    