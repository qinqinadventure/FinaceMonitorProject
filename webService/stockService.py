from crawler import stockinfo

# 根据code获取股票信息
def getStockInfoByCode(code:int):
    info = stockinfo.get_stock_base_info(code)
    return info