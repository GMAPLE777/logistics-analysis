"""应用配置"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', f'sqlite:///{BASE_DIR / "data" / "logistics.db"}'
    )
    DATA_DIR = BASE_DIR / 'data'
    RAW_DIR = DATA_DIR / 'raw'
    PROCESSED_DIR = DATA_DIR / 'processed'
    OUTPUT_DIR = DATA_DIR / 'output'
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
