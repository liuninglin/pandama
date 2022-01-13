import environ

env = environ.Env()

MONGODB_URL = 'mongodb://' + env.str("MONGO_USER") + ':' + env.str("MONGO_AUTH") + '@' + env.str("MONGO_HOST") + '/' + env.str("MONGO_DB") + '?authSource=admin&retryWrites=true&w=majority'
MONGODB_DB_ALIAS = env.str("MONGO_DB")