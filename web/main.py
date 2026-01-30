from fastapi import FastAPI
import uvicorn
# 导入router对象
from routers import analysis,k_lines,info
import json

app  = FastAPI()

# 各个模块包含到主应用
app.include_router(analysis.router)
app.include_router(k_lines.router)
app.include_router(info.router)

@app.get("/")
async def root():
    return {"message": "昌昌量化系统启动成功"}

# 启动主函数
def main():
    """
    主函数：启动FastAPI应用
    """
    # 获取启动配置
    run_cfg = json.load(open("config/db_setting.json"))

    uvicorn.run(
        "main:app",
        host=run_cfg["host"],  # 允许外部访问
        port=run_cfg["port"],       # 端口号
        reload=run_cfg["reload"]      # 开发模式：代码修改自动重启
    )

if __name__ == "__main__":
    main()