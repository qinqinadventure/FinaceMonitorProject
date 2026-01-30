from fastapi import APIRouter
import webService.analysisService as analysisService

# 创建路由实例，可以设置标签，前缀
router = APIRouter(prefix="/kline", tags=["获取k线"])

router.get("/min")
async def get_min_kline(stockcode:int):
    pass

router.get("/day")
async def get_day_kline(stockcode:int):
    pass

router.get("/week")
async def get_week_kline(stockcode:int):
    pass

router.get("/month")
async def get_month_kline(stockcode:int):
    pass