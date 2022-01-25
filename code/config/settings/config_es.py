import environ

env = environ.Env()

ES_URL = env.str("ES_URL")
ES_INDEX_PRODUCTS = env.str("ES_INDEX_PRODUCTS")

