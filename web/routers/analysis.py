from fastapi import APIRouter
import webService.analysisService as analysisService
import webModel.analysis_single_model as analysis_single_model
import webModel.analysis_multi_model as analysis_multi_model
from typing import List

# 创建路由实例，可以设置标签，前缀
router = APIRouter(prefix="/analysis", tags=["股票分析"])

@router.post("/analy_single")
# 固定股票分析接口
async def analysis_single(item:analysis_single_model.singleItem):
    print("analysis_single post...")
    print(item)


@router.post("/analy_multi")
# 警告接口
async def analysis_multi(item:analysis_multi_model.MultiItem):
    print("analysis_multi post...")
    print(item)
    pass

@router.post("/alarm_all")
# 分析所有股票接口并获取告警
async def alarm_all():
    print("alarm_all post...")
    result = analysisService.alarm_all()
    return result