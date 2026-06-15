"""Flask 应用工厂"""

import logging

from flask import Flask, jsonify
from sqlalchemy import create_engine

from app.config import config

# 全局数据库引擎
engine = None

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
)


def create_app(config_name='default'):
    """创建并配置 Flask 应用"""
    global engine

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # 初始化数据库引擎
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

    # 注册 Blueprint
    from app.routes.stats import stats_bp
    from app.routes.analysis import analysis_bp
    from app.routes.data import data_bp

    app.register_blueprint(stats_bp, url_prefix='/api/stats')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    app.register_blueprint(data_bp, url_prefix='/api/data')

    # 健康检查
    @app.route('/health')
    def health():
        return jsonify({'status': 'ok'})

    return app
