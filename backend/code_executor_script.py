# -*- coding: utf-8 -*-
"""代码执行脚本包装器，只负责生成临时执行脚本，别把进程和容器调度塞进来。"""
from __future__ import annotations

import json
import tempfile

from backend.code_executor_result import RESULT_MARKER


def write_wrapper_script(code: str, data_filepath: str) -> str:
    wrapper = f"""# -*- coding: utf-8 -*-
import json
import warnings

warnings.filterwarnings("ignore")

RESULT = []
DATA_FILE = {json.dumps(data_filepath, ensure_ascii=False)}

import pandas as pd
import numpy as np
import os as _os

_ext = _os.path.splitext(DATA_FILE)[1].lower()
if _ext in ('.xlsx', '.xls'):
    df = pd.read_excel(DATA_FILE)
elif _ext == '.csv':
    df = pd.read_csv(DATA_FILE)
elif _ext == '.tsv':
    df = pd.read_csv(DATA_FILE, sep='\\t')
elif _ext == '.txt':
    with open(DATA_FILE, 'r', errors='replace') as _f:
        _first = _f.readline()
    df = pd.read_csv(DATA_FILE, sep='\\t' if '\\t' in _first else ',')
elif _ext in ('.sav', '.zsav'):
    import pyreadstat
    df, _ = pyreadstat.read_sav(DATA_FILE)
elif _ext == '.dta':
    import pyreadstat
    df, _ = pyreadstat.read_dta(DATA_FILE)
elif _ext == '.sas7bdat':
    import pyreadstat
    df, _ = pyreadstat.read_sas7bdat(DATA_FILE)
elif _ext == '.xpt':
    import pyreadstat
    df, _ = pyreadstat.read_xport(DATA_FILE)
elif _ext == '.parquet':
    df = pd.read_parquet(DATA_FILE)
elif _ext == '.json':
    df = pd.read_json(DATA_FILE)
else:
    df = pd.read_csv(DATA_FILE)

# ---- 用户代码开始 ----
{code}
# ---- 用户代码结束 ----

print({json.dumps(RESULT_MARKER, ensure_ascii=False)})
print(json.dumps(RESULT, ensure_ascii=False, default=str))
"""

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        delete=False,
        encoding="utf-8",
    ) as handle:
        handle.write(wrapper)
        return handle.name
