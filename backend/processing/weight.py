import pandas as pd


def handle(df, variables, params):
    weight_var = params.get('weight_var', '')
    if weight_var and weight_var in df.columns:
        w = pd.to_numeric(df[weight_var], errors='coerce').fillna(1)
        for col in variables:
            if col not in df.columns or col == weight_var:
                continue
            s = pd.to_numeric(df[col], errors='coerce')
            df[col] = s * w
        return df, f'已使用 {weight_var} 对选中变量加权'
    return df, '处理完成'

