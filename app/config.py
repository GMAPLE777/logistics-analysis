"""应用配置"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """基础配置"""
    SECRET_KEY = 'logistics-analysis-dev'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{BASE_DIR / "data" / "logistics.db"}'
    DATA_DIR = BASE_DIR / 'data'
    RAW_DIR = DATA_DIR / 'raw'
    PROCESSED_DIR = DATA_DIR / 'processed'
    OUTPUT_DIR = DATA_DIR / 'output'


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
