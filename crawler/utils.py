# 获取股票具体网页url
def getStockUrl(web,root_path,stockCode):
    # 如果是东方财富的股票，则
    if web == "dfcf":
        return root_path + "\\zs" + stockCode + ".html"

    else:
        return None
