"""Streamlit 物流数据分析看板 — 主入口"""

import sys
from pathlib import Path

# 将项目根目录加入 sys.path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from app.config import config

# 页面配置
st.set_page_config(
    page_title='物流数据分析看板',
    page_icon='📦',
    layout='wide',
    initial_sidebar_state='expanded',
)


@st.cache_resource
def get_engine():
    """获取数据库连接（缓存）"""
    cfg = config['default']
    return create_engine(cfg.SQLALCHEMY_DATABASE_URI)


@st.cache_data
def load_data():
    """加载全部订单数据（缓存）"""
    engine = get_engine()
    return pd.read_sql('SELECT * FROM orders', engine)


def render_metric_cards(row):
    """渲染指标卡片行"""
    cols = st.columns(len(row))
    for col, (label, value) in zip(cols, row.items()):
        col.metric(label, value)


# ==================== 主页 ====================

def main():
    st.title('📦 物流数据分析看板')
    st.caption('基于 Kaggle E-Commerce Shipping Data 的多维度物流运营分析')

    # 加载数据
    try:
        df = load_data()
    except Exception as e:
        st.error(f'数据加载失败: {e}')
        st.info('请先运行 `python scripts/init_db.py` 初始化数据库')
        return

    # 侧边栏筛选
    st.sidebar.header('筛选条件')
    warehouse = st.sidebar.multiselect(
        '仓库区块', df['warehouse_block'].unique(),
        default=df['warehouse_block'].unique()
    )
    shipment = st.sidebar.multiselect(
        '运输方式', df['mode_of_shipment'].unique(),
        default=df['mode_of_shipment'].unique()
    )
    importance = st.sidebar.multiselect(
        '商品重要性', df['product_importance'].unique(),
        default=df['product_importance'].unique()
    )

    # 筛选数据
    filtered = df[
        (df['warehouse_block'].isin(warehouse)) &
        (df['mode_of_shipment'].isin(shipment)) &
        (df['product_importance'].isin(importance))
    ]

    if len(filtered) == 0:
        st.warning('筛选结果为空，请调整筛选条件')
        return

    st.sidebar.markdown(f'**筛选后记录数: {len(filtered):,}**')

    # 核心指标
    total = len(filtered)
    on_time = (filtered['reached_on_time'] == 0).sum()
    on_time_rate = on_time / total * 100

    render_metric_cards({
        '总订单数': f'{total:,}',
        '准时订单数': f'{on_time:,}',
        '准时率': f'{on_time_rate:.1f}%',
        '平均商品成本': f'${filtered["cost_of_the_product"].mean():.0f}',
        '平均折扣': f'${filtered["discount_offered"].mean():.1f}',
        '平均客户评分': f'{filtered["customer_rating"].mean():.2f}',
    })

    st.divider()

    # 概览图表
    import plotly.express as px

    col1, col2 = st.columns(2)

    with col1:
        st.subheader('订单准时率分布')
        on_time_counts = filtered['reached_on_time'].value_counts()
        fig = px.pie(
            values=on_time_counts.values,
            names=['准时', '延迟'],
            color_discrete_sequence=['#4CAF50', '#F44336'],
            hole=0.4,
        )
        fig.update_traces(textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader('各仓库订单量')
        wh_counts = filtered['warehouse_block'].value_counts().sort_index()
        fig = px.bar(
            x=wh_counts.index, y=wh_counts.values,
            labels={'x': '仓库区块', 'y': '订单数'},
            color=wh_counts.values,
            color_continuous_scale='Blues',
        )
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader('运输方式对比')
        ship_stats = filtered.groupby('mode_of_shipment').agg(
            订单数=('reached_on_time', 'count'),
            准时率=('reached_on_time', lambda x: (x == 0).mean() * 100),
        ).round(1).reset_index()
        fig = px.bar(
            ship_stats, x='mode_of_shipment', y='订单数',
            color='准时率', text='准时率',
            color_continuous_scale='RdYlGn',
            labels={'mode_of_shipment': '运输方式'},
        )
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.subheader('商品重要性分布')
        imp_stats = filtered.groupby('product_importance').agg(
            订单数=('reached_on_time', 'count'),
            准时率=('reached_on_time', lambda x: (x == 0).mean() * 100),
        ).round(1).reset_index()
        fig = px.bar(
            imp_stats, x='product_importance', y='订单数',
            color='准时率', text='准时率',
            color_continuous_scale='RdYlGn',
            labels={'product_importance': '重要性'},
        )
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    # 底部信息
    st.divider()
    st.caption('数据来源: Kaggle E-Commerce Shipping Data | 物流数据分析系统 v1.0')


if __name__ == '__main__':
    main()
