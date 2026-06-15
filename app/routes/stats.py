"""统计概览 API"""

from flask import Blueprint, jsonify
from app.services.analyzer import LogisticsAnalyzer
from app.routes.data import load_orders_df

stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/overview')
def overview():
    """GET /api/stats/overview — 汇总指标"""
    df = load_orders_df()
    if df is None:
        return jsonify({'error': {'code': 'DATA_NOT_LOADED', 'message': '数据未加载，请先运行 init_db.py'}}), 500

    analyzer = LogisticsAnalyzer(df)
    stats = analyzer.basic_stats()
    return jsonify(stats)
