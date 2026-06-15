"""数据清洗模块测试"""

import pytest
import pandas as pd
import numpy as np
from app.services.data_cleaner import DataCleaner


@pytest.fixture
def sample_df():
    """生成测试用 DataFrame"""
    return pd.DataFrame({
        'id': range(1, 101),
        'name': ['item'] * 100,
        'value': np.random.uniform(10, 100, 100),
        'category': np.random.choice(['A', 'B', 'C'], 100),
    })


@pytest.fixture
def df_with_missing(sample_df):
    """带缺失值的 DataFrame"""
    df = sample_df.copy()
    df.loc[0:4, 'value'] = np.nan
    df.loc[10:14, 'category'] = np.nan
    return df


@pytest.fixture
def df_with_duplicates(sample_df):
    """带重复行的 DataFrame"""
    df = pd.concat([sample_df, sample_df.iloc[:10]], ignore_index=True)
    return df


class TestDataCleaner:
    """DataCleaner 测试"""

    def test_info(self, sample_df):
        cleaner = DataCleaner(sample_df)
        report = cleaner.info()
        assert report['shape'] == (100, 4)
        assert 'id' in report['columns']
        assert report['duplicates'] == 0

    def test_handle_missing_auto_numeric(self, df_with_missing):
        cleaner = DataCleaner(df_with_missing)
        df, log = cleaner.handle_missing(strategy='auto').clean()
        assert df['value'].isnull().sum() == 0

    def test_handle_missing_auto_categorical(self, df_with_missing):
        cleaner = DataCleaner(df_with_missing)
        df, log = cleaner.handle_missing(strategy='auto').clean()
        assert df['category'].isnull().sum() == 0

    def test_handle_missing_drop(self, df_with_missing):
        cleaner = DataCleaner(df_with_missing)
        df, log = cleaner.handle_missing(strategy='drop').clean()
        assert len(df) < len(df_with_missing)

    def test_handle_duplicates(self, df_with_duplicates):
        cleaner = DataCleaner(df_with_duplicates)
        df, log = cleaner.handle_duplicates().clean()
        assert len(df) == 100

    def test_handle_outliers_iqr(self, sample_df):
        df = sample_df.copy()
        df.loc[0, 'value'] = 9999  # 注入异常值
        cleaner = DataCleaner(df)
        df, log = cleaner.handle_outliers(['value'], method='iqr').clean()
        assert df['value'].max() < 9999

    def test_rename_columns(self, sample_df):
        cleaner = DataCleaner(sample_df)
        df, log = cleaner.rename_columns({'value': 'amount'}).clean()
        assert 'amount' in df.columns
        assert 'value' not in df.columns

    def test_chaining(self, df_with_missing):
        """测试链式调用"""
        cleaner = DataCleaner(df_with_missing)
        df, log = cleaner.handle_missing().handle_duplicates().clean()
        assert df.isnull().sum().sum() == 0
