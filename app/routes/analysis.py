"""分析 API"""

from flask import Blueprint, jsonify, request
from app.services.analyzer import LogisticsAnalyzer
from app.routes.data import load_orders_df

analysis_bp = Blueprint('analysis', __name__)


def _get_analyzer():
    df = load_orders_df()
    if df is None:
        return None
    return LogisticsAnalyzer(df)


@analysis_bp.route('/delivery')
def delivery():
    """GET /api/analysis/delivery?group_by=warehouse_block"""
    analyzer = _get_analyzer()
    if analyzer is None:
        return jsonify({'error': '数据未加载'}), 500

    group_by = request.args.get('group_by', 'warehouse_block')
    valid = ('warehouse_block', 'mode_of_shipment', 'product_importance', 'gender')
    if group_by not in valid:
        return jsonify({'error': f'无效的 group_by，可选: {valid}'}), 400

    result = analyzer.delivery_by_dimension(group_by)
    return jsonify(result.to_dict(orient='records'))


@analysis_bp.route('/cost')
def cost():
    """GET /api/analysis/cost — 成本分析"""
    analyzer = _get_analyzer()
    if analyzer is None:
        return jsonify({'error': '数据未加载'}), 500

    result = analyzer.cost_analysis()
    return jsonify({
        'discount_impact': result['discount_impact'].to_dict(orient='records'),
        'weight_impact': result['weight_impact'].to_dict(orient='records'),
    })


@analysis_bp.route('/correlation')
def correlation():
    """GET /api/analysis/correlation — 相关性矩阵"""
    analyzer = _get_analyzer()
    if analyzer is None:
        return jsonify({'error': '数据未加载'}), 500

    corr = analyzer.correlation_analysis()
    return jsonify(corr.to_dict())


@analysis_bp.route('/customer')
def customer():
    """GET /api/analysis/customer — 客户分析"""
    analyzer = _get_analyzer()
    if analyzer is None:
        return jsonify({'error': '数据未加载'}), 500

    result = analyzer.customer_analysis()
    return jsonify({
        'purchase_impact': result['purchase_impact'].to_dict(orient='records'),
        'calls_impact': result['calls_impact'].to_dict(orient='records'),
    })


@analysis_bp.route('/insights')
def insights():
    """GET /api/analysis/insights — 自动生成洞察"""
    analyzer = _get_analyzer()
    if analyzer is None:
        return jsonify({'error': '数据未加载'}), 500

    analyzer.generate_summary()
    return jsonify({'insights': analyzer.get_insights()})
