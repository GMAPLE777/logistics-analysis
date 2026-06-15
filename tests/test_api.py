"""Flask API 测试"""

import pytest
import sys
from pathlib import Path

import pandas as pd
import numpy as np
from sqlalchemy import create_engine

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import create_app
from app.models.order import Base


@pytest.fixture
def test_db(tmp_path):
    """创建测试数据库并填充数据"""
    db_path = tmp_path / 'test.db'
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)

    # 生成测试数据
    np.random.seed(42)
    n = 100
    df = pd.DataFrame({
        'warehouse_block': np.random.choice(['A', 'B', 'C'], n),
        'mode_of_shipment': np.random.choice(['Ship', 'Flight'], n),
        'customer_care_calls': np.random.randint(2, 6, n),
        'customer_rating': np.random.randint(1, 6, n),
        'cost_of_the_product': np.round(np.random.uniform(50, 500, n), 2),
        'prior_purchases': np.random.randint(0, 5, n),
        'product_importance': np.random.choice(['low', 'medium', 'high'], n),
        'gender': np.random.choice(['M', 'F'], n),
        'discount_offered': np.round(np.random.uniform(1, 50, n), 2),
        'weight_in_gms': np.round(np.random.uniform(500, 5000, n), 2),
        'reached_on_time': np.random.choice([0, 1], n),
    })
    df.to_sql('orders', engine, index=False)
    return db_path


@pytest.fixture
def client(test_db):
    """创建测试客户端"""
    app = create_app('development')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{test_db}'

    # 重新初始化引擎
    import app as app_module
    from sqlalchemy import create_engine as ce
    app_module.engine = ce(f'sqlite:///{test_db}')

    with app.test_client() as client:
        yield client


class TestHealthAPI:
    """健康检查测试"""

    def test_health(self, client):
        resp = client.get('/health')
        assert resp.status_code == 200
        assert resp.get_json()['status'] == 'ok'


class TestStatsAPI:
    """统计 API 测试"""

    def test_overview_returns_json(self, client):
        resp = client.get('/api/stats/overview')
        assert resp.content_type == 'application/json'
        assert resp.status_code == 200

    def test_overview_structure(self, client):
        resp = client.get('/api/stats/overview')
        data = resp.get_json()
        assert 'total_orders' in data
        assert 'on_time_rate' in data
        assert data['total_orders'] == 100


class TestAnalysisAPI:
    """分析 API 测试"""

    def test_delivery_default(self, client):
        resp = client.get('/api/analysis/delivery')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_delivery_with_group_by(self, client):
        resp = client.get('/api/analysis/delivery?group_by=mode_of_shipment')
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 2  # Ship, Flight

    def test_delivery_invalid_group_by(self, client):
        resp = client.get('/api/analysis/delivery?group_by=invalid')
        assert resp.status_code == 400
        assert 'error' in resp.get_json()

    def test_cost(self, client):
        resp = client.get('/api/analysis/cost')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'discount_impact' in data
        assert 'weight_impact' in data

    def test_correlation(self, client):
        resp = client.get('/api/analysis/correlation')
        assert resp.status_code == 200

    def test_insights(self, client):
        resp = client.get('/api/analysis/insights')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'insights' in data
        assert isinstance(data['insights'], list)


class TestDataAPI:
    """数据查询 API 测试"""

    def test_orders_pagination(self, client):
        resp = client.get('/api/data/orders?page=1&per_page=10')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'data' in data
        assert 'total' in data
        assert data['total'] == 100
        assert len(data['data']) == 10
        assert data['has_next'] is True
        assert data['has_prev'] is False

    def test_orders_per_page_limit(self, client):
        resp = client.get('/api/data/orders?per_page=500')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['per_page'] <= 200

    def test_orders_negative_page(self, client):
        resp = client.get('/api/data/orders?page=-1')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['page'] == 1  # 被修正为 1

    def test_field_stats(self, client):
        resp = client.get('/api/data/orders/stats')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'warehouse_block' in data
        assert data['warehouse_block']['type'] == 'categorical'
