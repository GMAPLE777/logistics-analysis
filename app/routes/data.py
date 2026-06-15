"""数据查询 API + 数据加载工具"""

import logging

import pandas as pd
from flask import Blueprint, jsonify, request
from sqlalchemy import text
from app import engine

logger = logging.getLogger(__name__)

data_bp = Blueprint('data', __name__)

# 缓存 DataFrame，避免每次请求都读数据库
_df_cache = None


def load_orders_df():
    """从数据库加载全部订单为 DataFrame（带缓存）"""
    global _df_cache
    if _df_cache is not None:
        return _df_cache

    if engine is None:
        logger.error('数据库引擎未初始化')
        return None

    try:
        _df_cache = pd.read_sql('SELECT * FROM orders', engine)
        logger.info('从数据库加载 %d 条订单', len(_df_cache))
        return _df_cache
    except Exception as e:
        logger.error('加载订单数据失败: %s', e)
        return None


def invalidate_cache():
    """清除缓存（数据更新后调用）"""
    global _df_cache
    _df_cache = None
    logger.info('DataFrame 缓存已清除')


@data_bp.route('/orders')
def list_orders():
    """GET /api/data/orders?page=1&per_page=50"""
    if engine is None:
        return jsonify({'error': {'code': 'DB_NOT_READY', 'message': '数据库未初始化'}}), 500

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    # 参数校验
    page = max(page, 1)
    per_page = max(min(per_page, 200), 1)

    offset = (page - 1) * per_page

    try:
        with engine.connect() as conn:
            count_result = conn.execute(text('SELECT COUNT(*) FROM orders'))
            total = count_result.scalar()

            result = conn.execute(
                text('SELECT * FROM orders LIMIT :limit OFFSET :offset'),
                {'limit': per_page, 'offset': offset}
            )
            columns = result.keys()
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
    except Exception as e:
        logger.error('查询订单失败: %s', e)
        return jsonify({'error': {'code': 'QUERY_FAILED', 'message': '查询失败'}}), 500

    total_pages = (total + per_page - 1) // per_page

    return jsonify({
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': total_pages,
        'has_next': page < total_pages,
        'has_prev': page > 1,
        'data': rows,
    })


@data_bp.route('/orders/stats')
def field_stats():
    """GET /api/data/orders/stats — 各字段分布统计"""
    df = load_orders_df()
    if df is None:
        return jsonify({'error': {'code': 'DATA_NOT_LOADED', 'message': '数据未加载'}}), 500

    stats = {}
    for col in df.columns:
        if col in ('id', 'created_at'):
            continue
        if df[col].dtype in ('int64', 'float64'):
            stats[col] = {
                'type': 'numeric',
                'mean': round(df[col].mean(), 2),
                'median': round(df[col].median(), 2),
                'min': round(df[col].min(), 2),
                'max': round(df[col].max(), 2),
                'std': round(df[col].std(), 2),
            }
        else:
            stats[col] = {
                'type': 'categorical',
                'unique': int(df[col].nunique()),
                'top_values': df[col].value_counts().head(5).to_dict(),
            }

    return jsonify(stats)
