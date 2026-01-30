import json

def jsonToDict(json_path):
    """
    将JSON文件内容读取并转换为Python字典。

    Args:
        json_path (str): JSON文件的路径。

    Returns:
        dict: 从JSON文件解析得到的字典。

    Raises:
        FileNotFoundError: 当指定的文件路径不存在时引发。
        json.JSONDecodeError: 当文件内容不是有效的JSON格式时引发。
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file) # 使用json.load()方法从文件对象解析数据[2,5,10](@ref)
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"错误：文件 '{json_path}' 未找到。")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"错误：文件 '{json_path}' 不是有效的JSON格式。详情：{e.msg}", e.doc, e.pos)