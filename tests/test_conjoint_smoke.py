# -*- coding: utf-8 -*-
"""联合分析冒烟测试：验证重构后的输出结构。"""
import unittest

import numpy as np
import pandas as pd

from backend.analysis.methods import conjoint


class ConjointSmokeTest(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        n = 100
        self.df = pd.DataFrame({
            'score': np.random.randint(1, 10, n),
            '品牌': np.random.choice(['A', 'B', 'C'], n),
            '价格': np.random.choice(['高', '中', '低'], n),
        })

    def test_basic_run(self):
        result = conjoint.run(self.df, {'score_var': 'score', 'attribute_vars': ['品牌', '价格']})
        self.assertIn('sections', result)
        self.assertEqual(result['name'], '联合分析')
        sections = result['sections']
        titles = [s['title'] for s in sections]
        self.assertIn('联合分析结果汇总', titles)
        self.assertIn('联合分析(Conjoint Analysis)估计结果', titles)
        self.assertIn('模型拟合', titles)
        self.assertIn('联合分析模型拟合度', titles)
        # 汇总表有5列
        self.assertEqual(len(sections[0]['headers']), 5)

    def test_estimate_result_has_intercept(self):
        result = conjoint.run(self.df, {'score_var': 'score', 'attribute_vars': ['品牌', '价格']})
        est_section = [s for s in result['sections'] if s['title'] == '联合分析(Conjoint Analysis)估计结果'][0]
        first_row = est_section['rows'][0]
        self.assertEqual(first_row[0], '截距')

    def test_save_utility(self):
        result = conjoint.run(self.df, {
            'score_var': 'score',
            'attribute_vars': ['品牌', '价格'],
            'save_utility': True,
        })
        self.assertIn('new_columns', result)
        names = [c['name'] for c in result['new_columns']]
        self.assertIn('效用值_品牌', names)
        self.assertIn('效用值_价格', names)

    def test_save_residual(self):
        result = conjoint.run(self.df, {
            'score_var': 'score',
            'attribute_vars': ['品牌', '价格'],
            'save_residual': True,
        })
        self.assertIn('new_columns', result)
        names = [c['name'] for c in result['new_columns']]
        self.assertIn('预测值', names)
        self.assertIn('残差', names)
        # 预测值表出现
        titles = [s['title'] for s in result['sections']]
        self.assertIn('预测值与残差', titles)

    def test_pie_chart(self):
        result = conjoint.run(self.df, {'score_var': 'score', 'attribute_vars': ['品牌', '价格']})
        chart_sections = [s for s in result['sections'] if s['type'] == 'charts']
        self.assertTrue(len(chart_sections) > 0)
        chart = chart_sections[0]['charts'][0]
        self.assertEqual(chart['chartType'], 'category_distribution')
        self.assertEqual(chart['title'], '属性重要性占比')

    def test_anova(self):
        result = conjoint.run(self.df, {'score_var': 'score', 'attribute_vars': ['品牌', '价格']})
        anova_sections = [s for s in result['sections'] if '方差分析' in s['title']]
        self.assertTrue(len(anova_sections) > 0)

    def test_model_fit_three_levels(self):
        result = conjoint.run(self.df, {'score_var': 'score', 'attribute_vars': ['品牌', '价格']})
        fit_section = [s for s in result['sections'] if s['title'] == '模型拟合'][0]
        self.assertEqual(len(fit_section['rows']), 3)  # 0阶/1阶/2阶
        self.assertIn('0阶', fit_section['rows'][0][0])
        self.assertIn('1阶', fit_section['rows'][1][0])
        self.assertIn('2阶', fit_section['rows'][2][0])

    def test_insufficient_vars(self):
        result = conjoint.run(self.df, {'score_var': 'score', 'attribute_vars': ['品牌']})
        self.assertIn('至少需要', result['description'])

    def test_missing_score_var(self):
        result = conjoint.run(self.df, {'score_var': 'nonexistent', 'attribute_vars': ['品牌', '价格']})
        self.assertIn('不存在', result['description'])


if __name__ == '__main__':
    unittest.main()
