import environ

root = environ.Path(__file__) - 3
env = environ.Env()
env.read_env(env_file=root('.env.prod'))

from config.settings.base import * 