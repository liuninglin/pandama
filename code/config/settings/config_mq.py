import environ

env = environ.Env()

MQ_BROKER_URL = env('MQ_BROKER_URL')
