import environ

root = environ.Path(__file__) - 3
env = environ.Env()
environ.Env.read_env()


MONGODB_URL = 'mongodb+srv://' + env.str("MONGO_USER") + ':' + env.str("MONGO_AUTH") + '@' + env.str("MONGO_HOST") + '/' + env.str("MONGO_DB") + '?retryWrites=true&w=majority'
MONGODB_DB_ALIAS = env.str("MONGO_DB")