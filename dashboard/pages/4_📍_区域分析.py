"""区域分析页 — 仓库区块对比"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
import plotly.express as px
from dashboard.app import load_data
from app.services.analyzer import LogisticsAnalyzer

st.set_page_config(page_title='区域分析', page_icon='📍', layout='wide')

st.title('📍 仓库区块分析')

try:
    df = load_data()
except Exception as e:
    st.error(f'数据未加载: {e}')
    st.stop()

analyzer = LogisticsAnalyzer(df)

# 仓库区块分析
st.subheader('各仓库区块运营指标')
wh = analyzer.delivery_by_dimension('warehouse_block')

col1, col2 = st.columns(2)

with col1:
    fig = px.bar(
        wh, x='warehouse_block', y='order_count',
        color='on_time_rate',
        color_continuous_scale='RdYlGn',
        text='on_time_rate',
        labels={'warehouse_block': '仓库', 'order_count': '订单数', 'on_time_rate': '准时率(%)'},
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.bar(
        wh, x='warehouse_block', y='avg_cost',
        text='avg_cost',
        labels={'warehouse_block': '仓库', 'avg_cost': '平均成本($)'},
        color='avg_cost',
        color_continuous_scale='Blues',
    )
    fig.update_traces(texttemplate='$%{text:.0f}', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# 仓库 × 运输方式交叉分析
st.subheader('仓库 × 运输方式 准时率热力图')
cross = df.groupby(['warehouse_block', 'mode_of_shipment']).agg(
    准时率=('reached_on_time', lambda x: round((x == 0).mean() * 100, 1)),
    订单数=('reached_on_time', 'count'),
).reset_index()

pivot = cross.pivot(index='warehouse_block', columns='mode_of_shipment', values='准时率')
fig = px.imshow(
    pivot, text_auto='.1f',
    color_continuous_scale='RdYlGn',
    labels={'x': '运输方式', 'y': '仓库区块', 'color': '准时率(%)'},
)
st.plotly_chart(fig, use_container_width=True)

# 详细数据
st.subheader('详细数据')
st.dataframe(wh, use_container_width=True, hide_index=True)
