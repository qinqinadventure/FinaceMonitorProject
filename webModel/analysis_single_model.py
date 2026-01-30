from pydantic import BaseModel
from typing import Optional,List

# 分析单个股票模型
class singleItem(BaseModel):
    # 股票号码
    stock_code: str

    # 获取股票号码
    def getStockCode(self):
        return self.stock_code
    