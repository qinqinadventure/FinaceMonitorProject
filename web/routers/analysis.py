from fastapi import APIRouter
import webService.analysisService as analysisService
import webModel.analysis_single_model as analysis_single_model

# 创建路由实例，可以设置标签，前缀
router = APIRouter(prefix="/analysis", tags=["股票分析"])


router.get("/analy_single")
# 固定股票分析接口
async def analysis_single(item:analysis_single_model):



