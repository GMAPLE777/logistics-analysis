"""概览页 — 核心指标 + 数据质量"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
import plotly.express as px
from dashboard.app import load_data

st.set_page_config(page_title='概览', page_icon='📊', layout='wide')

st.title('📊 数据概览')

try:
    df = load_data()
except Exception:
    st.error('数据未加载')
    st.stop()

# 数据质量
st.subheader('数据质量')
col1, col2, col3, col4 = st.columns(4)
col1.metric('总记录数', f'{len(df):,}')
col2.metric('字段数', len(df.columns))
col3.metric('缺失值总数', int(df.isnull().sum().sum()))
col4.metric('重复行数', int(df.duplicated().sum()))

# 各字段缺失情况
missing = df.isnull().sum()
if missing.sum() > 0:
    st.bar_chart(missing[missing > 0])

st.divider()

# 数值字段统计
st.subheader('数值字段统计')
numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
st.dataframe(df[numeric_cols].describe().round(2), use_container_width=True)

st.divider()

# 分类字段分布
st.subheader('分类字段分布')
cat_cols = df.select_dtypes(include=['object']).columns
for col in cat_cols:
    st.markdown(f'**{col}**')
    counts = df[col].value_counts()
    fig = px.bar(x=counts.index, y=counts.values, labels={'x': col, 'y': '数量'})
    st.plotly_chart(fig, use_container_width=True)
