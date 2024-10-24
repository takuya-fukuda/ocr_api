# api/__init__.py
#from api.config import LocalConfig
from api.config import config

config = {
    "local": config.LocalConfig
}