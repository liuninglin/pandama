import environ

root = environ.Path(__file__) - 3
env = environ.Env()
environ.Env.read_env()


NEO4J_URI = env('NEO4J_URI')
NEO4J_USER = env('NEO4J_USER')
NEO4J_PASSWORD = env('NEO4J_PASSWORD')

