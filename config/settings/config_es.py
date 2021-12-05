import environ

root = environ.Path(__file__) - 3
env = environ.Env()
environ.Env.read_env()


ES_URL = env.str("ES_URL")
ES_INDEX_PRODUCTS = env.str("ES_INDEX_PRODUCTS")

