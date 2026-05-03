import numpy as np
import pandas as pd


def handle(df, variables, params):
    name = params.get('name', 'new_var')
    expr = params.get('expr', '')
    if not expr:
        return df, '处理完成'

    local_vars = {col: df[col] for col in df.columns}
    local_vars.update({'log': np.log, 'sqrt': np.sqrt, 'abs': np.abs, 'mean': np.mean, 'sum': np.sum, 'np': np, 'pd': pd})
    try:
        df[name] = eval(expr, {"__builtins__": {}}, local_vars)
    except Exception as e:
        raise ValueError(f'公式计算错误: {str(e)}') from e
    return df, f'已生成新变量 {name}'

