"""订单数据模型 — 映射 Kaggle E-Commerce Shipping Data"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Index, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Order(Base):
    """物流订单表"""
    __tablename__ = 'orders'
    __table_args__ = (
        Index('idx_warehouse_block', 'warehouse_block'),
        Index('idx_mode_of_shipment', 'mode_of_shipment'),
        Index('idx_product_importance', 'product_importance'),
        Index('idx_reached_on_time', 'reached_on_time'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    warehouse_block = Column(String(1), nullable=False, comment='仓库区块 A-F')
    mode_of_shipment = Column(String(10), nullable=False, comment='运输方式 Ship/Flight/Road')
    customer_care_calls = Column(Integer, default=0, comment='客服呼叫次数')
    customer_rating = Column(Integer, default=3, comment='客户评分 1-5')
    cost_of_the_product = Column(Float, nullable=False, comment='商品成本')
    prior_purchases = Column(Integer, default=0, comment='历史购买次数')
    product_importance = Column(String(10), default='medium', comment='商品重要性 low/medium/high')
    gender = Column(String(6), nullable=False, comment='客户性别')
    discount_offered = Column(Float, default=0, comment='折扣金额')
    weight_in_gms = Column(Float, nullable=False, comment='商品重量(克)')
    reached_on_time = Column(Integer, nullable=False, comment='是否准时 0=准时 1=延迟')
    created_at = Column(DateTime, server_default=func.now(), comment='入库时间')

    def to_dict(self):
        return {
            'id': self.id,
            'warehouse_block': self.warehouse_block,
            'mode_of_shipment': self.mode_of_shipment,
            'customer_care_calls': self.customer_care_calls,
            'customer_rating': self.customer_rating,
            'cost_of_the_product': self.cost_of_the_product,
            'prior_purchases': self.prior_purchases,
            'product_importance': self.product_importance,
            'gender': self.gender,
            'discount_offered': self.discount_offered,
            'weight_in_gms': self.weight_in_gms,
            'reached_on_time': self.reached_on_time,
        }

    def __repr__(self):
        return f'<Order {self.id}>'
