from fastapi import FastAPI
# 导入router对象
from routers import analysis,k_lines

app  = FastAPI()

# 各个模块包含到主应用
app.include_router(analysis.router)
app.include_router(k_lines.router)

@app.get("/")
async def root():
    return {"message": "昌昌量化系统启动成功"}