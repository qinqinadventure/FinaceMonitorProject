from fastapi import APIRouter
from webModel.stock_info_model import StockInfo
import webService.stockService as stockService

router = APIRouter(prefix="/info", tags=["获取信息"])

# 2. 使用Pydantic模型作为参数
@router.post("/stockinfo")
async def get_stock_info(request: StockInfo):
    """
    根据股票代码获取股票信息
    """
    print(f"收到股票代码请求: {request.stockcode}")
    result = stockService.getStockInfoByCode(request.stockcode)
    return {
        "status": "success",
        "code": request.stockcode,
        "data": result
    }