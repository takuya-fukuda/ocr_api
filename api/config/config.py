import os
from pathlib import Path

basedir = Path(__file__).parent.parent

class LocalConfig:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///local.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 追跡を無効化