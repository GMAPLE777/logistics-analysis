"""
初始化数据库 — 创建表结构 + 导入 Kaggle 数据

用法:
    python scripts/init_db.py                       # 使用默认数据文件
    python scripts/init_db.py --file my_data.csv    # 指定数据文件
"""

import sys
import argparse
from pathlib import Path

# 将项目根目录加入 sys.path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd
from sqlalchemy import create_engine, inspect
from app.config import config
from app.models.order import Base


def clean_columns(df):
    """统一列名：小写 + 下划线"""
    rename_map = {
        'ID': 'id',
        'Warehouse_block': 'warehouse_block',
        'Mode_of_Shipment': 'mode_of_shipment',
        'Customer_care_calls': 'customer_care_calls',
        'Customer_rating': 'customer_rating',
        'Cost_of_the_Product': 'cost_of_the_product',
        'Prior_purchases': 'prior_purchases',
        'Product_importance': 'product_importance',
        'Gender': 'gender',
        'Discount_offered': 'discount_offered',
        'Weight_in_gms': 'weight_in_gms',
        'Reached.on.Time_Y.N': 'reached_on_time',
    }
    df.rename(columns=rename_map, inplace=True)

    # 删除原始 id 列（数据库自动生成）
    if 'id' in df.columns:
        df.drop(columns=['id'], inplace=True)

    return df


def init_database(csv_path=None):
    """初始化数据库"""
    cfg = config['development']
    db_path = cfg.SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')

    print(f'[init_db] 数据库路径: {db_path}')

    # 创建引擎 + 建表
    engine = create_engine(cfg.SQLALCHEMY_DATABASE_URI)
    Base.metadata.create_all(engine)
    print('[init_db] 表结构创建完成')

    # 查找数据文件
    if csv_path is None:
        raw_dir = cfg.RAW_DIR
        csv_files = list(raw_dir.glob('*.csv'))
        if not csv_files:
            print(f'[init_db] 未找到数据文件，请将 CSV 放到 {raw_dir}/')
            print('[init_db] 推荐数据集: https://www.kaggle.com/datasets/prachi13shrestha/ecommerce-shipping-data')
            return
        csv_path = csv_files[0]

    print(f'[init_db] 数据文件: {csv_path}')

    # 读取数据
    df = pd.read_csv(csv_path, encoding='utf-8')
    print(f'[init_db] 读取 {len(df)} 行数据')

    # 列名标准化
    df = clean_columns(df)

    # 写入数据库
    df.to_sql('orders', engine, if_exists='replace', index=False)
    print(f'[init_db] 成功导入 {len(df)} 条记录到 orders 表')

    # 验证
    inspector = inspect(engine)
    columns = inspector.get_columns('orders')
    print(f'[init_db] 表字段: {[c["name"] for c in columns]}')

    count = pd.read_sql('SELECT COUNT(*) as cnt FROM orders', engine)
    print(f'[init_db] 数据库中记录数: {count["cnt"].values[0]}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='初始化物流分析数据库')
    parser.add_argument('--file', type=str, help='CSV 文件路径', default=None)
    args = parser.parse_args()

    csv_path = Path(args.file) if args.file else None
    init_database(csv_path)
