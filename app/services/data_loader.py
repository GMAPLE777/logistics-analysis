"""数据加载模块 — 读取 CSV/Excel，返回 DataFrame"""

import pandas as pd
from pathlib import Path


class DataLoader:
    """数据加载器"""

    def __init__(self, data_dir='data'):
        self.data_dir = Path(data_dir)

    def load_csv(self, filename, encoding='utf-8'):
        """加载 CSV 文件"""
        filepath = self.data_dir / 'raw' / filename
        if not filepath.exists():
            raise FileNotFoundError(f'数据文件不存在: {filepath}')
        df = pd.read_csv(filepath, encoding=encoding)
        print(f'[DataLoader] 加载 {filename}，共 {len(df)} 行，{len(df.columns)} 列')
        return df

    def load_excel(self, filename, sheet_name=0):
        """加载 Excel 文件"""
        filepath = self.data_dir / 'raw' / filename
        if not filepath.exists():
            raise FileNotFoundError(f'数据文件不存在: {filepath}')
        df = pd.read_excel(filepath, sheet_name=sheet_name)
        print(f'[DataLoader] 加载 {filename}，共 {len(df)} 行，{len(df.columns)} 列')
        return df

    def load(self, filename):
        """根据后缀自动选择加载方式"""
        ext = Path(filename).suffix.lower()
        if ext == '.csv':
            return self.load_csv(filename)
        elif ext in ('.xlsx', '.xls'):
            return self.load_excel(filename)
        else:
            raise ValueError(f'不支持的文件格式: {ext}')

    def save_csv(self, df, filename, folder='processed'):
        """保存 DataFrame 为 CSV"""
        filepath = self.data_dir / folder / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f'[DataLoader] 已保存到 {filepath}')
        return filepath
