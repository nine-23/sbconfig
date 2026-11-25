# 导入你的协议解析模块（按你实际的 protocol 目录位置调整导入路径）
from copy import deepcopy

from app.protocol import vless
import re

PROTOCOL_MAP = {
    "vless": vless,
    # 后续有 trojan、vmess 等继续往这里加
}

# 1. 定义各地区对应的关键词映射
REGION_RULES = {
    "🇭🇰": ["HK", "香港"],
    "🇸🇬": ["SG", "新加坡"],
    "🇯🇵": ["JP", "日本"],
    "🇺🇸": ["US", "美国"],
    "🇬🇧": ["GB", "英国", "GB"],
}

# 1. 建立安全组名映射：{'G0': '🇭🇰', 'G1': '🇸🇬', ...}
group_to_emoji = {f"G{i}": emoji for i, emoji in enumerate(REGION_RULES.keys())}


def replace_node(node: dict) -> tuple:

    # 2. 动态生成命名捕获组正则：(?P<HK>HK|香港)|(?P<TW>TW|台湾)|...
    pattern_str = "|".join(
        f"(?P<G{i}>{'|'.join(map(re.escape, words))})"
        for i, words in enumerate(REGION_RULES.values())
    )
    pattern = re.compile(pattern_str, re.I)

    # 3. 匹配并返回对应地区结果
    match = pattern.search(node["tag"])
    if match:
        emoji = group_to_emoji[match.lastgroup]
        node_proxy = deepcopy(node)
        node["tag"] = f"{emoji} - {node['tag']}"

        # 删除原有节点的反代ip，
        # 复制相同的ip 加上相同区域的反代路径
        try:
            node_proxy["transport"]["path"] = (
                f"ProxyIP.{REGION_RULES[emoji][0]}.CMLiussss.net"
            )
            node_proxy["tag"] = f"{emoji} - PROXY-IP - {node_proxy['tag']}"
            node["transport"]["path"] = "/"
        except IndexError:
            return node, False

        return node, node_proxy

    return node, False


def main(subscription) -> list:
    used_tags = set()
    node_outbounds: list[dict] = []
    subscription = subscription.splitlines()
    for line in subscription:
        line = line.strip()
        if not line or "://" not in line:
            continue
        protocol_type = line.partition("://")[0].lower()
        handler = PROTOCOL_MAP.get(protocol_type)

        if not handler:
            continue

        node = handler.main(line, used_tags)
        if node:
            node, node_proxy = replace_node(node)
            if node_proxy:
                node_outbounds.append(node_proxy)
            node_outbounds.append(node)

    return node_outbounds
