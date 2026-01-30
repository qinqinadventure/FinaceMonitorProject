from pydantic import BaseModel
from typing import Optional,List

# 分析多个股票模型
class MultiItem(BaseModel):
    # 多个股票列表
    stock_code_list: List[int]