"""生成模拟物流订单数据（Kaggle E-Commerce Shipping Data 格式）"""

import pandas as pd
import numpy as np
from pathlib import Path

np.random.seed(42)

def generate_data(n=10999):
    """生成模拟数据"""
    data = {
        'Warehouse_block': np.random.choice(['A', 'B', 'C', 'D', 'F'], n, p=[0.15, 0.2, 0.25, 0.2, 0.2]),
        'Mode_of_Shipment': np.random.choice(['Ship', 'Flight', 'Road'], n, p=[0.5, 0.3, 0.2]),
        'Customer_care_calls': np.random.randint(2, 8, n),
        'Customer_rating': np.random.randint(1, 6, n),
        'Cost_of_the_Product': np.round(np.random.uniform(50, 500, n), 2),
        'Prior_purchases': np.random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 10], n),
        'Product_importance': np.random.choice(['low', 'medium', 'high'], n, p=[0.4, 0.4, 0.2]),
        'Gender': np.random.choice(['M', 'F'], n),
        'Discount_offered': np.round(np.random.exponential(10, n).clip(1, 100), 2),
        'Weight_in_gms': np.round(np.random.uniform(100, 8000, n), 2),
    }

    # 准时率与折扣/重量相关（模拟真实规律）
    base_prob = 0.6
    discount_effect = -0.003 * data['Discount_offered']
    weight_effect = -0.00002 * data['Weight_in_gms']
    importance_map = {'low': 0.05, 'medium': 0, 'high': -0.05}
    importance_effect = np.array([importance_map[x] for x in data['Product_importance']])

    prob = (base_prob + discount_effect + weight_effect + importance_effect).clip(0.2, 0.9)
    data['Reached.on.Time_Y.N'] = (np.random.random(n) > prob).astype(int)

    df = pd.DataFrame(data)
    df.insert(0, 'ID', range(1, n + 1))
    return df


if __name__ == '__main__':
    df = generate_data(10999)
    output_dir = Path(__file__).resolve().parent.parent / 'data' / 'raw'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'ecommerce_shipping.csv'
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f'生成 {len(df)} 条模拟数据 -> {output_path}')
    print(f'字段: {list(df.columns)}')
    print(f'准时率: {(df["Reached.on.Time_Y.N"] == 0).mean() * 100:.1f}%')
