"""成本分析页 — 折扣/重量对准时率的影响"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
import plotly.express as px
from dashboard.app import load_data
from app.services.analyzer import LogisticsAnalyzer

st.set_page_config(page_title='成本分析', page_icon='💰', layout='wide')

st.title('💰 成本与折扣分析')

try:
    df = load_data()
except Exception as e:
    st.error(f'数据未加载: {e}')
    st.stop()

analyzer = LogisticsAnalyzer(df)
cost = analyzer.cost_analysis()

# 折扣影响
st.subheader('折扣区间 vs 准时率')
disc = cost['discount_impact']

col1, col2 = st.columns(2)

with col1:
    fig = px.bar(
        disc, x='discount_range', y='order_count',
        color='on_time_rate',
        color_continuous_scale='RdYlGn',
        text='on_time_rate',
        labels={'discount_range': '折扣区间', 'order_count': '订单数', 'on_time_rate': '准时率(%)'},
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.line(
        disc, x='discount_range', y='on_time_rate',
        markers=True,
        labels={'discount_range': '折扣区间', 'on_time_rate': '准时率(%)'},
    )
    fig.update_traces(line_color='#FF9800', line_width=3)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# 重量影响
st.subheader('商品重量 vs 准时率')
weight = cost['weight_impact']

col3, col4 = st.columns(2)

with col3:
    fig = px.bar(
        weight, x='weight_range', y='order_count',
        color='on_time_rate',
        color_continuous_scale='RdYlGn',
        text='on_time_rate',
        labels={'weight_range': '重量区间', 'order_count': '订单数', 'on_time_rate': '准时率(%)'},
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

with col4:
    fig = px.line(
        weight, x='weight_range', y='on_time_rate',
        markers=True,
        labels={'weight_range': '重量区间', 'on_time_rate': '准时率(%)'},
    )
    fig.update_traces(line_color='#2196F3', line_width=3)
    st.plotly_chart(fig, use_container_width=True)

# 散点图：成本 vs 折扣
st.subheader('成本 vs 折扣 散点图')
sample = df.sample(min(2000, len(df)))
fig = px.scatter(
    sample, x='cost_of_the_product', y='discount_offered',
    color=sample['reached_on_time'].map({0: '准时', 1: '延迟'}),
    color_discrete_sequence=['#4CAF50', '#F44336'],
    labels={'x': '商品成本', 'y': '折扣金额', 'color': '送达状态'},
    opacity=0.6,
)
st.plotly_chart(fig, use_container_width=True)
