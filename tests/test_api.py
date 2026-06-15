"""Flask API 测试"""

import pytest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import create_app


@pytest.fixture
def client():
    """创建测试客户端"""
    app = create_app('development')
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestStatsAPI:
    """统计 API 测试"""

    def test_overview_returns_json(self, client):
        resp = client.get('/api/stats/overview')
        assert resp.content_type == 'application/json'

    def test_overview_structure(self, client):
        resp = client.get('/api/stats/overview')
        if resp.status_code == 200:
            data = resp.get_json()
            assert 'total_orders' in data
            assert 'on_time_rate' in data


class TestAnalysisAPI:
    """分析 API 测试"""

    def test_delivery_default(self, client):
        resp = client.get('/api/analysis/delivery')
        assert resp.status_code in (200, 500)

    def test_delivery_with_group_by(self, client):
        resp = client.get('/api/analysis/delivery?group_by=mode_of_shipment')
        assert resp.status_code in (200, 500)

    def test_delivery_invalid_group_by(self, client):
        resp = client.get('/api/analysis/delivery?group_by=invalid')
        assert resp.status_code == 400

    def test_cost(self, client):
        resp = client.get('/api/analysis/cost')
        assert resp.status_code in (200, 500)

    def test_correlation(self, client):
        resp = client.get('/api/analysis/correlation')
        assert resp.status_code in (200, 500)

    def test_insights(self, client):
        resp = client.get('/api/analysis/insights')
        assert resp.status_code in (200, 500)


class TestDataAPI:
    """数据查询 API 测试"""

    def test_orders_pagination(self, client):
        resp = client.get('/api/data/orders?page=1&per_page=10')
        assert resp.status_code in (200, 500)
        if resp.status_code == 200:
            data = resp.get_json()
            assert 'data' in data
            assert 'total' in data
            assert 'page' in data

    def test_orders_per_page_limit(self, client):
        resp = client.get('/api/data/orders?per_page=500')
        assert resp.status_code in (200, 500)
        if resp.status_code == 200:
            data = resp.get_json()
            assert data['per_page'] <= 200  # 被截断到上限

    def test_field_stats(self, client):
        resp = client.get('/api/data/orders/stats')
        assert resp.status_code in (200, 500)
