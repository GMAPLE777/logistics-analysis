"""Flask 应用工厂"""

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from app.config import config

# 全局数据库会话
engine = None
SessionLocal = None


def create_app(config_name='default'):
    """创建并配置 Flask 应用"""
    global engine, SessionLocal

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # 初始化数据库
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    SessionLocal = scoped_session(sessionmaker(bind=engine))

    # 注册 Blueprint
    from app.routes.stats import stats_bp
    from app.routes.analysis import analysis_bp
    from app.routes.data import data_bp

    app.register_blueprint(stats_bp, url_prefix='/api/stats')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    app.register_blueprint(data_bp, url_prefix='/api/data')

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        if SessionLocal:
            SessionLocal.remove()

    return app
