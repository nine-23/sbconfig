import json
import re
from app import config
from app import requests


def findtemp(number_temp: int):
    """
    note: 按照仓库编号 查找模板文件路径
    number_temp: 模板所处编号 模板格式为 1-config.json 2.config.json 格式
    """

    temp_list: list[str] = [i.name for i in config.TEMPDIR.glob("*.json")]
    if not temp_list:
        raise FileExistsError("模板文件夹没有文件")

    temp_list = sorted(
        temp_list,
        key=lambda x: int(m.group()) if (m := re.search(r"\d+", x)) else 0,
    )
    idx = number_temp - 1
    if idx < 0 or idx >= len(temp_list):
        result = {str(i + 1): v for i, v in enumerate(temp_list)}
        raise IndexError(f"没有这个编号，请输入编号: {result}")
    config.TEMP_OK = config.TEMPDIR / temp_list[idx]


def main(input_temp: str = "") -> None:
    if input_temp.startswith(("http://", "https://")):
        try:
            response = requests.get(input_temp, timeout=10)
            # status_code 是整数 200，不是字符串
            if response.status_code == 200:
                config.TEMP_DATA = response.json()
                return
            raise requests.HTTPError(f"模板链接请求错误: HTTP {response.status_code}")
        except Exception as e:
            raise requests.HTTPError(f"模板链接异常: {e}")

    if input_temp and input_temp.isdigit():
        findtemp(int(input_temp))

    if not config.TEMP_OK.exists() or config.TEMP_OK.is_dir():
        raise FileExistsError("默认模板文件不存在，请传入模板文件")

    try:
        with open(config.TEMP_OK, "r", encoding="utf-8") as f:
            config.TEMP_DATA = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise ValueError(f"JSON 格式错误: {e}")
