# 物流数据分析系统

基于 Kaggle E-Commerce Shipping Data 的物流运营分析平台。Flask 后端提供 RESTful API，Streamlit 提供交互式数据看板。

## 技术栈

| 层级 | 技术 |
|------|------|
| 数据存储 | SQLite + SQLAlchemy |
| 后端 API | Flask + Blueprint |
| 数据看板 | Streamlit + Plotly |
| 数据处理 | Pandas + NumPy |
| 可视化 | Matplotlib + Seaborn + Plotly |
| 测试 | pytest |

## 项目结构

```
logistics-analysis/
├── app/                        # Flask 后端
│   ├── models/                 # SQLAlchemy 模型
│   ├── routes/                 # API 路由（stats/analysis/data）
│   └── services/               # 业务逻辑（loader/cleaner/analyzer）
├── dashboard/                  # Streamlit 看板
│   ├── app.py                  # 主入口
│   └── pages/                  # 5 个分析页面
├── data/
│   ├── raw/                    # 原始数据（Kaggle CSV）
│   ├── processed/              # 清洗后数据
│   └── output/                 # 图表 + 报告
├── scripts/                    # 工具脚本
├── tests/                      # 单元测试
└── run.py                      # Flask 启动入口
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 下载数据集

从 [Kaggle](https://www.kaggle.com/datasets/prachi13shrestha/ecommerce-shipping-data) 下载数据集，将 CSV 文件放到 `data/raw/` 目录。

### 3. 初始化数据库

```bash
python scripts/init_db.py
```

### 4. 启动 Flask 后端

```bash
python run.py
# → http://localhost:5000
```

### 5. 启动 Streamlit 看板

```bash
streamlit run dashboard/app.py
# → http://localhost:8501
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/stats/overview` | 汇总指标 |
| GET | `/api/analysis/delivery?group_by=warehouse_block` | 按维度分析准时率 |
| GET | `/api/analysis/cost` | 成本分析 |
| GET | `/api/analysis/correlation` | 相关性矩阵 |
| GET | `/api/analysis/customer` | 客户行为分析 |
| GET | `/api/analysis/insights` | 自动生成洞察 |
| GET | `/api/data/orders?page=1&per_page=50` | 分页查询订单 |
| GET | `/api/data/orders/stats` | 字段分布统计 |

## 看板页面

| 页面 | 功能 |
|------|------|
| 📊 概览 | 核心指标 + 数据质量 |
| 🚚 时效分析 | 按仓库/运输方式/重要性的准时率 |
| 💰 成本分析 | 折扣/重量对准时率的影响 |
| 📍 区域分析 | 仓库区块对比 + 交叉分析 |
| 📈 深度分析 | 相关性矩阵 + 客户行为 + 自动洞察 |

## 运行测试

```bash
pytest tests/ -v
```

## 数据集

使用 [Kaggle E-Commerce Shipping Data](https://www.kaggle.com/datasets/prachi13shrestha/ecommerce-shipping-data)，包含约 11,000 条物流订单记录，12 个字段：

- 仓库区块、运输方式、客户评分、商品成本、折扣、重量、是否准时送达等

## License

MIT
