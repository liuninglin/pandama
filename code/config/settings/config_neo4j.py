import environ

env = environ.Env()

NEO4J_URI = env('NEO4J_URI')
NEO4J_USER = env('NEO4J_USER')
NEO4J_PASSWORD = env('NEO4J_PASSWORD')

