# 导入你的协议解析模块（按你实际的 protocol 目录位置调整导入路径）
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


def replace_node(node: dict):

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
        node["tag"] = f"{emoji} - {node['tag']}"

        # 若有加上反代地址
        try:
            node["transport"]["path"] = (
                f"ProxyIP.{REGION_RULES[emoji][0]}.CMLiussss.net"
            )
            node["tag"] = f"{node['tag']} - PROXY-IP"
        except IndexError:
            pass

    return node


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
            node = replace_node(node)
            node_outbounds.append(node)

    return node_outbounds
