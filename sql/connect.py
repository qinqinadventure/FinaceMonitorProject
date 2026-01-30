import pymysql
import pymysql.cursors
from pymysql.cursors import DictCursor
import logging

# 配置日志，便于记录错误信息
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger('db_operations')

# 创建连接对象
def getSqlConnect(
        host='localhost',      # 数据库服务器地址
        user='root',   # 数据库用户名
        password='123456', # 数据库密码
        database='finace', # 要连接的数据库名称
        port=3306,             # 端口号，默认为3306
):
    connection = pymysql.connect(
        host = host,      # 数据库服务器地址
        user = user,   # 数据库用户名
        password = password, # 数据库密码
        database = database, # 要连接的数据库名称
        port = port ,             # 端口号，默认为3306
        charset='utf8mb4',     # 字符编码，避免中文乱码
        cursorclass=pymysql.cursors.DictCursor # 设置游标类型，返回字典形式的结果
    )
    return connection


# 执行sql语句
def executeSQL(sql, params=None, max_retries=3):
    """
    执行SQL语句的增强版函数，包含异常处理和重试机制。

    Args:
        sql (str): 要执行的SQL语句。
        params (tuple|dict|None): SQL语句的参数，用于参数化查询，默认为None。
        max_retries (int): 连接失败时的最大重试次数，默认为1。

    Returns:
        tuple: (success, result)
        - success (bool): 执行是否成功。
        - result: 成功时为查询结果（如fetchone的值），失败时为None或错误信息。
    """
    connection = None
    retries = 0

    while retries <= max_retries:
        try:
            # 尝试建立数据库连接
            connection = getSqlConnect()  # 假设这是您获取连接的函数
            with connection.cursor(cursor=DictCursor) as cursor:  # 使用字典游标
                cursor.execute(sql, params)  # 使用参数化查询，防止SQL注入

                # 判断是否为查询操作并获取结果
                if sql.strip().lower().startswith('select'):
                    result = cursor.fetchone()  # 或 fetchall()/fetchmany()
                else:
                    connection.commit()  # 非查询操作，提交事务
                    result = f"操作成功，影响行数: {cursor.rowcount}"

                return (True, result)  # 执行成功，返回结果

        except pymysql.MySQLError as e:
            # 记录详细的错误日志，方便排查
            logger.error(
                f"数据库错误 (尝试 {retries + 1}/{max_retries + 1}): SQL-> {sql}, 参数-> {params}, 错误信息-> {e}")

            if connection:
                connection.rollback()  # 出现异常，回滚事务 [1](@ref)

            # 如果是连接问题且可重试，则进行重试
            if e.args[0] in (2003, 2006, 2013) and retries < max_retries:  # 常见的连接错误码 [4](@ref)
                retries += 1
                logger.info(f"等待重试... (第{retries}次)")
                continue
            else:
                # 重试次数已用完或其他错误，返回失败
                return (False, f"数据库操作失败: {e}")

        except Exception as e:
            # 捕获非数据库相关的意外错误
            logger.error(f"未知错误: {e}")
            if connection:
                connection.rollback()
            return (False, f"发生未知错误: {e}")

        finally:
            # 无论成功与否，最终都要确保连接被关闭
            if connection:
                connection.close()

    return (False, "重试次数已用完，连接失败。")  # 理论上不会执行到这，为保险起见