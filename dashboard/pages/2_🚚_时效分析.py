"""时效分析页 — 按仓库/运输方式/重要性的准时率分析"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
import plotly.express as px
from dashboard.app import load_data
from app.services.analyzer import LogisticsAnalyzer

st.set_page_config(page_title='时效分析', page_icon='🚚', layout='wide')

st.title('🚚 配送时效分析')

try:
    df = load_data()
except Exception as e:
    st.error(f'数据未加载: {e}')
    st.stop()

analyzer = LogisticsAnalyzer(df)
basic = analyzer.basic_stats()

# 核心指标
col1, col2, col3 = st.columns(3)
col1.metric('准时订单数', f'{basic["on_time_orders"]:,}')
col2.metric('延迟订单数', f'{basic["late_orders"]:,}')
col3.metric('准时率', f'{basic["on_time_rate"]}%')

st.divider()

# 按维度分析
dimension = st.selectbox(
    '选择分析维度',
    ['warehouse_block', 'mode_of_shipment', 'product_importance', 'gender'],
    format_func=lambda x: {
        'warehouse_block': '仓库区块',
        'mode_of_shipment': '运输方式',
        'product_importance': '商品重要性',
        'gender': '客户性别',
    }.get(x, x)
)

result = analyzer.delivery_by_dimension(dimension)

col1, col2 = st.columns(2)

with col1:
    st.subheader(f'按 {dimension} 的订单量')
    fig = px.bar(
        result, x=dimension, y='order_count',
        color='on_time_rate',
        color_continuous_scale='RdYlGn',
        text='on_time_rate',
        labels={dimension: dimension, 'order_count': '订单数', 'on_time_rate': '准时率(%)'},
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader(f'按 {dimension} 的准时率')
    fig = px.bar(
        result, x=dimension, y='on_time_rate',
        color='on_time_rate',
        color_continuous_scale='RdYlGn',
        text='on_time_rate',
        labels={dimension: dimension, 'on_time_rate': '准时率(%)'},
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.add_hline(y=basic['on_time_rate'], line_dash='dash', line_color='red',
                  annotation_text=f'整体均值 {basic["on_time_rate"]}%')
    st.plotly_chart(fig, use_container_width=True)

# 明细表
st.subheader('详细数据')
st.dataframe(result, use_container_width=True, hide_index=True)
