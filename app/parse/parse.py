from app.parse import subscribe, node
from app import config


def main(sub, allow_local_file):
    config.SUBSCRIPTION = subscribe.main(sub, allow_local_file)

    if not config.SUBSCRIPTION:
        raise ValueError("解析订阅后，数据为空")

    config.NODE = node.main(config.SUBSCRIPTION)

    if not config.NODE:
        raise ValueError("订阅不符合 sing-box outbounds，结果为空")
