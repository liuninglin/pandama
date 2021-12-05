import environ

root = environ.Path(__file__) - 3
env = environ.Env()
environ.Env.read_env()


MQ_BROKER_URL = env('MQ_BROKER_URL')
