"""趋势分析页 — 相关性分析 + 客户行为"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from dashboard.app import load_data
from app.services.analyzer import LogisticsAnalyzer

st.set_page_config(page_title='趋势分析', page_icon='📈', layout='wide')

st.title('📈 深度分析')

try:
    df = load_data()
except Exception as e:
    st.error(f'数据未加载: {e}')
    st.stop()

analyzer = LogisticsAnalyzer(df)

# 相关性分析
st.subheader('变量相关性矩阵')
corr = analyzer.correlation_analysis()

fig = px.imshow(
    corr, text_auto='.2f',
    color_continuous_scale='RdBu_r',
    zmin=-1, zmax=1,
    labels={'color': '相关系数'},
)
fig.update_layout(width=700, height=600)
st.plotly_chart(fig, use_container_width=False)

st.divider()

# 客户行为分析
st.subheader('客户行为分析')
customer = analyzer.customer_analysis()

col1, col2 = st.columns(2)

with col1:
    st.markdown('**历史购买次数 vs 准时率**')
    purchase = customer['purchase_impact']
    fig = px.line(
        purchase, x='prior_purchases', y='on_time_rate',
        markers=True,
        labels={'prior_purchases': '历史购买次数', 'on_time_rate': '准时率(%)'},
    )
    fig.update_traces(line_color='#2196F3', line_width=3)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown('**客服呼叫次数 vs 准时率**')
    calls = customer['calls_impact']
    fig = px.line(
        calls, x='customer_care_calls', y='on_time_rate',
        markers=True,
        labels={'customer_care_calls': '客服呼叫次数', 'on_time_rate': '准时率(%)'},
    )
    fig.update_traces(line_color='#FF9800', line_width=3)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# 客户评分分布
st.subheader('客户评分分布')
rating_dist = df['customer_rating'].value_counts().sort_index()
fig = px.bar(
    x=rating_dist.index, y=rating_dist.values,
    labels={'x': '评分', 'y': '订单数'},
    color=rating_dist.values,
    color_continuous_scale='Viridis',
)
st.plotly_chart(fig, use_container_width=True)

# 自动洞察
st.divider()
st.subheader('💡 分析洞察')
insights = analyzer.get_insights()
for insight in insights:
    st.markdown(f'- {insight}')
