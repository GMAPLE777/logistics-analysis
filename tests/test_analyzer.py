"""数据分析模块测试"""

import pytest
import pandas as pd
import numpy as np
from app.services.analyzer import LogisticsAnalyzer


@pytest.fixture
def orders_df():
    """生成模拟订单数据"""
    np.random.seed(42)
    n = 500
    return pd.DataFrame({
        'id': range(1, n + 1),
        'warehouse_block': np.random.choice(['A', 'B', 'C', 'D', 'F'], n),
        'mode_of_shipment': np.random.choice(['Ship', 'Flight', 'Road'], n),
        'customer_care_calls': np.random.randint(2, 8, n),
        'customer_rating': np.random.randint(1, 6, n),
        'cost_of_the_product': np.round(np.random.uniform(50, 500, n), 2),
        'prior_purchases': np.random.randint(0, 10, n),
        'product_importance': np.random.choice(['low', 'medium', 'high'], n),
        'gender': np.random.choice(['M', 'F'], n),
        'discount_offered': np.round(np.random.uniform(0, 50, n), 2),
        'weight_in_gms': np.round(np.random.uniform(500, 5000, n), 2),
        'reached_on_time': np.random.choice([0, 1], n, p=[0.6, 0.4]),
    })


class TestLogisticsAnalyzer:
    """LogisticsAnalyzer 测试"""

    def test_basic_stats(self, orders_df):
        analyzer = LogisticsAnalyzer(orders_df)
        stats = analyzer.basic_stats()
        assert stats['total_orders'] == 500
        assert 'on_time_rate' in stats
        assert 0 <= stats['on_time_rate'] <= 100
        assert stats['avg_cost'] > 0

    def test_delivery_by_dimension(self, orders_df):
        analyzer = LogisticsAnalyzer(orders_df)
        result = analyzer.delivery_by_dimension('warehouse_block')
        assert len(result) > 0
        assert 'on_time_rate' in result.columns
        assert 'order_count' in result.columns

    def test_delivery_by_shipment(self, orders_df):
        analyzer = LogisticsAnalyzer(orders_df)
        result = analyzer.delivery_by_dimension('mode_of_shipment')
        assert len(result) == 3  # Ship, Flight, Road

    def test_cost_analysis(self, orders_df):
        analyzer = LogisticsAnalyzer(orders_df)
        result = analyzer.cost_analysis()
        assert 'discount_impact' in result
        assert 'weight_impact' in result

    def test_correlation_analysis(self, orders_df):
        analyzer = LogisticsAnalyzer(orders_df)
        corr = analyzer.correlation_analysis()
        assert corr.shape[0] == corr.shape[1]  # 方阵
        assert abs(corr.loc['reached_on_time', 'reached_on_time']) == 1.0  # 对角线为1

    def test_customer_analysis(self, orders_df):
        analyzer = LogisticsAnalyzer(orders_df)
        result = analyzer.customer_analysis()
        assert 'purchase_impact' in result
        assert 'calls_impact' in result

    def test_generate_summary(self, orders_df):
        analyzer = LogisticsAnalyzer(orders_df)
        results = analyzer.generate_summary()
        assert 'basic' in results
        assert 'delivery' in results
        assert 'cost' in results
        assert 'correlation' in results
        assert 'customer' in results

    def test_get_insights(self, orders_df):
        analyzer = LogisticsAnalyzer(orders_df)
        analyzer.generate_summary()
        insights = analyzer.get_insights()
        assert isinstance(insights, list)
        assert len(insights) > 0
