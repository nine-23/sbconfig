import threading
from app.parse import parse
from app.main import generated
from app import config
from copy import deepcopy

_CONFIG_LOCK = threading.Lock()


def _reset_state() -> None:
    """强制重置所有运行时全局状态"""
    config.TEMP_OK = config.DEFAULT_TEMP
    config.UPLAD_UA = ""
    config.TEMP_DATA = {}
    config.SINGBOX_CONFIG = {}
    config.SUBSCRIPTION = ""
    config.NODE = []


def generate_config(sub_input: str, input_temp: str = "", header="") -> dict:
    """专供 Vercel 接口调用的入口，复用 base 模块逻辑"""
    with _CONFIG_LOCK:
        _reset_state()
        config.UPLAD_UA = header
        try:
            # 1. 解析订阅（Web 接口禁止读取服务器本地文件)
            parse.main(sub_input, allow_local_file=False)
            # 2. 读取模板
            generated.main(input_temp)
            # 返回深拷贝，断开与全局变量的引用
            return deepcopy(config.TEMP_DATA)
        finally:
            # 无论是否报错，释放锁前必清空全局状态
            _reset_state()


def cli() -> None:

    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="将订阅输出到 sing-box 配置中| 目前只支持解析 vless 协议"
    )
    # parser.add_argument("-n", "--notui", action="store_true", help="关闭 fzf 界面")
    parser.add_argument(
        "-s",
        "--subscription",
        default="",
        help="订阅链接：base64或http链接或者完整订阅配置",
    )
    parser.add_argument(
        "-in",
        "--input",
        default="",
        help="sing-box 配置模板， json 文件",
    )
    args = parser.parse_args()
    try:
        parse.main(args.subscription, allow_local_file=True)
    except Exception as e:
        print(1, config.SUBSCRIPTION)
        print(e)
    try:
        generated.main(args.input)
    except Exception as e:
        print(config.TEMP_OK)
        print(config.TEMP_DATA)
        print(e)

    with open(config.OUT_CONFIG, "w", encoding="utf-8") as f:
        json.dump(config.TEMP_DATA, f, ensure_ascii=False, indent=2)
