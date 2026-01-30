from pydantic import BaseModel

# 1. 定义请求体模型
class StockInfo(BaseModel):
    stockcode: str  # 股票代码应该是字符串类型（包含前导零）