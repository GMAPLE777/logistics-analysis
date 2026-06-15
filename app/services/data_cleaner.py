"""数据清洗模块 — 缺失值、异常值、重复值处理"""

import logging

import pandas as pd
import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)


class DataCleaner:
    """数据清洗器"""

    def __init__(self, df):
        self.df = df.copy()
        self.log = []

    def info(self):
        """输出数据概览"""
        report = {
            'shape': self.df.shape,
            'columns': list(self.df.columns),
            'dtypes': self.df.dtypes.to_dict(),
            'missing': self.df.isnull().sum().to_dict(),
            'duplicates': int(self.df.duplicated().sum()),
        }
        return report

    def handle_missing(self, strategy='auto'):
        """
        处理缺失值
        strategy: auto(按类型自动) | drop(删除行) | fill_mean | fill_median | fill_mode
        """
        for col in self.df.columns:
            n_missing = self.df[col].isnull().sum()
            if n_missing == 0:
                continue

            pct = n_missing / len(self.df) * 100

            if strategy == 'auto':
                if pct > 30:
                    self.df.drop(columns=[col], inplace=True)
                    self.log.append(f'删除列 {col}（缺失率 {pct:.1f}%）')
                elif self.df[col].dtype in ('int64', 'float64'):
                    median = self.df[col].median()
                    self.df[col].fillna(median, inplace=True)
                    self.log.append(f'列 {col} 用中位数 {median} 填充 {n_missing} 条')
                else:
                    mode = self.df[col].mode()
                    if len(mode) > 0:
                        self.df[col].fillna(mode[0], inplace=True)
                        self.log.append(f'列 {col} 用众数 "{mode[0]}" 填充 {n_missing} 条')
                    else:
                        self.df.drop(columns=[col], inplace=True)
                        self.log.append(f'删除列 {col}（全为缺失值）')
            elif strategy == 'drop':
                self.df.dropna(subset=[col], inplace=True)
                self.log.append(f'删除列 {col} 中 {n_missing} 行缺失值')
            elif strategy == 'fill_mean':
                self.df[col].fillna(self.df[col].mean(), inplace=True)
            elif strategy == 'fill_median':
                self.df[col].fillna(self.df[col].median(), inplace=True)
            elif strategy == 'fill_mode':
                self.df[col].fillna(self.df[col].mode()[0], inplace=True)

        return self

    def handle_duplicates(self):
        """删除重复行"""
        n = self.df.duplicated().sum()
        if n > 0:
            self.df.drop_duplicates(inplace=True)
            self.log.append(f'删除 {n} 条重复记录')
        return self

    def handle_outliers(self, columns, method='iqr', threshold=1.5):
        """
        处理异常值
        method: iqr(四分位距截断) | zscore(Z-score 删除)
        """
        for col in columns:
            if col not in self.df.columns:
                continue
            if self.df[col].dtype not in ('int64', 'float64'):
                continue

            if method == 'iqr':
                q1 = self.df[col].quantile(0.25)
                q3 = self.df[col].quantile(0.75)
                iqr = q3 - q1
                lower = q1 - threshold * iqr
                upper = q3 + threshold * iqr
                n_outliers = ((self.df[col] < lower) | (self.df[col] > upper)).sum()
                if n_outliers > 0:
                    self.df[col] = self.df[col].clip(lower, upper)
                    self.log.append(f'列 {col} IQR 截断 {n_outliers} 个异常值')

            elif method == 'zscore':
                col_data = self.df[col].dropna()
                z = np.abs(stats.zscore(col_data))
                n_outliers = (z > threshold).sum()
                if n_outliers > 0:
                    outlier_idx = col_data.index[z > threshold]
                    self.df = self.df.drop(index=outlier_idx).copy()
                    self.log.append(f'列 {col} Z-score 删除 {n_outliers} 个异常值')

        return self

    def rename_columns(self, mapping):
        """重命名列"""
        self.df.rename(columns=mapping, inplace=True)
        self.log.append(f'重命名列: {mapping}')
        return self

    def clean(self):
        """执行清洗，返回清洗后的 DataFrame 和日志"""
        logger.info('清洗完成，共 %d 项操作:', len(self.log))
        for entry in self.log:
            logger.info('  - %s', entry)
        logger.info('  最终数据形状: %s', self.df.shape)
        return self.df, self.log
