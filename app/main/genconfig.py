from copy import deepcopy
from app import config


def all_node(in_temp: list, node_tag: str, index: int) -> bool:
    if "#all" in in_temp:
        config.TEMP_DATA["outbounds"][index]["outbounds"].append(node_tag)
        return True
    return False


def join_node(in_temp: list, node_tag: str, index: int) -> None:
    # 1. 先检查排除规则（-），只要命中任意排除词直接跳过该节点
    for field in in_temp:
        if field.startswith("-"):
            for tag in field[1:].split("|"):
                if tag and tag in node_tag:
                    return
    # 2. 再检查包含规则（+），命中后添加一次即结束，避免重复添加
    for field in in_temp:
        if field.startswith("+"):
            for tag in field[1:].split("|"):
                if tag and tag in node_tag:
                    config.TEMP_DATA["outbounds"][index]["outbounds"].append(node_tag)
                    return


def main() -> None:
    outbounds = deepcopy(config.TEMP_DATA["outbounds"])
    direct_tag = ""
    for i in outbounds:
        if i.get("type") == "direct":
            direct_tag = i.get("tag", "")
            break
    for index, bounds in enumerate(outbounds):
        if "outbounds" not in bounds:
            # 跳过 direct / block / dns 等不含子出站列表的节点
            continue

        # 初始化 outbounds
        outbound: list[str] = bounds["outbounds"]
        for tag in outbound:
            if tag.startswith(("+", "-", "#")):
                config.TEMP_DATA["outbounds"][index]["outbounds"].remove(tag)
        for node in config.NODE:
            node_tag = node["tag"]
            if all_node(outbound, node_tag, index):
                continue
            join_node(outbound, node_tag, index)
        if not config.TEMP_DATA["outbounds"][index]["outbounds"]:
            if not direct_tag:
                raise ValueError(
                    f"outbounds[{index}] 没有匹配的标签，且缺少 direct 出站兜底",
                )
            config.TEMP_DATA["outbounds"][index]["outbounds"].append(direct_tag)
    # 将解析出的所有具体节点对象追加到最终的 outbounds 列表中
    config.TEMP_DATA["outbounds"].extend(config.NODE)
