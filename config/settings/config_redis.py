import environ

env = environ.Env()

# Redis
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://" + env.str("REDIS_HOST") + ":" + env.str("REDIS_PORT") + "/" + env.str("REDIS_DB"),
        "OPTIONS": {
            "PASSWORD": env.str("REDIS_AUTH"),
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

REDIS_HOST = env.str("REDIS_HOST")
REDIS_PORT = env.str("REDIS_PORT")
REDIS_DB = env.str("REDIS_DB")
REDIS_AUTH = env.str("REDIS_AUTH")
