"""数据分析模块 — 物流指标计算与多维分析"""

import pandas as pd
import numpy as np


class LogisticsAnalyzer:
    """物流数据分析器"""

    def __init__(self, df):
        self.df = df.copy()
        self.results = {}

    # ==================== 基础统计 ====================

    def basic_stats(self):
        """汇总指标"""
        total = len(self.df)
        on_time = (self.df['reached_on_time'] == 0).sum()

        stats = {
            'total_orders': total,
            'on_time_orders': int(on_time),
            'late_orders': int(total - on_time),
            'on_time_rate': round(on_time / total * 100, 2),
            'avg_cost': round(self.df['cost_of_the_product'].mean(), 2),
            'total_cost': round(self.df['cost_of_the_product'].sum(), 2),
            'avg_discount': round(self.df['discount_offered'].mean(), 2),
            'avg_weight': round(self.df['weight_in_gms'].mean(), 2),
            'avg_rating': round(self.df['customer_rating'].mean(), 2),
            'avg_calls': round(self.df['customer_care_calls'].mean(), 2),
        }
        self.results['basic'] = stats
        return stats

    # ==================== 时效分析 ====================

    def delivery_by_dimension(self, dimension='warehouse_block'):
        """按维度分析准时率"""
        result = self.df.groupby(dimension).agg(
            order_count=('id', 'count'),
            on_time_count=('reached_on_time', lambda x: (x == 0).sum()),
            on_time_rate=('reached_on_time', lambda x: round((x == 0).mean() * 100, 2)),
            avg_cost=('cost_of_the_product', 'mean'),
            avg_discount=('discount_offered', 'mean'),
            avg_weight=('weight_in_gms', 'mean'),
            avg_rating=('customer_rating', 'mean'),
        ).round(2)

        result = result.sort_values('on_time_rate', ascending=False).reset_index()
        self.results[f'delivery_by_{dimension}'] = result
        return result

    def delivery_analysis(self):
        """综合时效分析"""
        analysis = {
            'by_warehouse': self.delivery_by_dimension('warehouse_block'),
            'by_shipment': self.delivery_by_dimension('mode_of_shipment'),
            'by_importance': self.delivery_by_dimension('product_importance'),
            'by_gender': self.delivery_by_dimension('gender'),
        }
        self.results['delivery'] = analysis
        return analysis

    # ==================== 成本分析 ====================

    def cost_analysis(self):
        """成本与折扣分析"""
        # 折扣对准时率的影响
        self.df['discount_range'] = pd.cut(
            self.df['discount_offered'],
            bins=[0, 5, 10, 20, 50, 100],
            labels=['0-5', '5-10', '10-20', '20-50', '50+']
        )
        discount_impact = self.df.groupby('discount_range', observed=True).agg(
            order_count=('id', 'count'),
            on_time_rate=('reached_on_time', lambda x: round((x == 0).mean() * 100, 2)),
            avg_cost=('cost_of_the_product', 'mean'),
        ).round(2).reset_index()

        # 重量与准时率
        self.df['weight_range'] = pd.cut(
            self.df['weight_in_gms'],
            bins=[0, 1000, 2000, 3000, 5000, 10000],
            labels=['<1kg', '1-2kg', '2-3kg', '3-5kg', '5kg+']
        )
        weight_impact = self.df.groupby('weight_range', observed=True).agg(
            order_count=('id', 'count'),
            on_time_rate=('reached_on_time', lambda x: round((x == 0).mean() * 100, 2)),
            avg_discount=('discount_offered', 'mean'),
        ).round(2).reset_index()

        analysis = {
            'discount_impact': discount_impact,
            'weight_impact': weight_impact,
        }
        self.results['cost'] = analysis
        return analysis

    # ==================== 相关性分析 ====================

    def correlation_analysis(self):
        """数值字段相关性矩阵"""
        numeric_cols = [
            'customer_care_calls', 'customer_rating', 'cost_of_the_product',
            'prior_purchases', 'discount_offered', 'weight_in_gms', 'reached_on_time'
        ]
        cols = [c for c in numeric_cols if c in self.df.columns]
        corr = self.df[cols].corr().round(3)
        self.results['correlation'] = corr
        return corr

    # ==================== 客户分析 ====================

    def customer_analysis(self):
        """客户行为分析"""
        # 历史购买次数与准时率
        purchase_impact = self.df.groupby('prior_purchases').agg(
            order_count=('id', 'count'),
            on_time_rate=('reached_on_time', lambda x: round((x == 0).mean() * 100, 2)),
            avg_rating=('customer_rating', 'mean'),
            avg_calls=('customer_care_calls', 'mean'),
        ).round(2).reset_index()

        # 客服呼叫与准时率
        calls_impact = self.df.groupby('customer_care_calls').agg(
            order_count=('id', 'count'),
            on_time_rate=('reached_on_time', lambda x: round((x == 0).mean() * 100, 2)),
        ).round(2).reset_index()

        analysis = {
            'purchase_impact': purchase_impact,
            'calls_impact': calls_impact,
        }
        self.results['customer'] = analysis
        return analysis

    # ==================== 综合报告 ====================

    def generate_summary(self):
        """生成完整分析结果"""
        self.basic_stats()
        self.delivery_analysis()
        self.cost_analysis()
        self.correlation_analysis()
        self.customer_analysis()
        return self.results

    def get_insights(self):
        """基于分析结果生成洞察"""
        if 'basic' not in self.results:
            self.basic_stats()
        if 'delivery' not in self.results:
            self.delivery_analysis()

        basic = self.results['basic']
        delivery = self.results['delivery']

        insights = []

        # 准时率洞察
        rate = basic['on_time_rate']
        if rate >= 80:
            insights.append(f'整体准时签收率为 {rate}%，表现良好')
        else:
            insights.append(f'整体准时签收率为 {rate}%，低于 80% 目标，需优化')

        # 仓库洞察
        wh = delivery['by_warehouse']
        best_wh = wh.iloc[0]
        worst_wh = wh.iloc[-1]
        insights.append(
            f'仓库 {best_wh["warehouse_block"]} 准时率最高（{best_wh["on_time_rate"]}%），'
            f'仓库 {worst_wh["warehouse_block"]} 最低（{worst_wh["on_time_rate"]}%）'
        )

        # 运输方式洞察
        ship = delivery['by_shipment']
        best_ship = ship.iloc[0]
        insights.append(
            f'运输方式 {best_ship["mode_of_shipment"]} 准时率最高（{best_ship["on_time_rate"]}%）'
        )

        # 折扣洞察
        if 'cost' in self.results:
            disc = self.results['cost']['discount_impact']
            if len(disc) > 1:
                high_disc = disc.iloc[-1]
                low_disc = disc.iloc[0]
                if high_disc['on_time_rate'] < low_disc['on_time_rate']:
                    insights.append('高折扣订单准时率明显低于低折扣订单，可能存在促销期间运力不足问题')

        return insights
