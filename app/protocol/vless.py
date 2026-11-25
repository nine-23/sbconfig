from typing import Any
from urllib.parse import unquote, urlparse, parse_qs


def main(vless_uri: str, used_tags: set) -> dict | None:
    """
    params:
        vless_uri: 单个 vless 链接
        used_tags: 标签集合
    """
    if not vless_uri.startswith("vless://"):
        return None

    parsed = urlparse(vless_uri)
    params = {k: v[0] for k, v in parse_qs(parsed.query).items()}

    # 处理节点名称并防止重名（sing-box 要求 tag 必须唯一）
    base_tag = unquote(parsed.fragment).strip() or f"{parsed.hostname}:{parsed.port}"
    tag = base_tag

    ## 主要方法， 当 used_tags 包含 tag 时修改tag， 加上数字
    counter = 1
    while tag in used_tags:
        tag = f"{base_tag}_{counter}"
        counter += 1
    used_tags.add(tag)

    outbound: dict[str, Any] = {
        "type": "vless",
        "tag": tag,
        "server": parsed.hostname,
        "server_port": parsed.port,
        "uuid": parsed.username,
    }

    # 1. 处理 Flow (如 xtls-rprx-vision)
    flow = params.get("flow")
    if flow:
        outbound["flow"] = flow

    # 2. 处理 TLS 与 Reality
    security = params.get("security", "none")
    if security in ("tls", "reality"):
        tls_config = {
            "enabled": True,
            "server_name": params.get("sni") or params.get("host") or parsed.hostname,
        }
        if params.get("allowInsecure") == "1" or params.get("insecure") == "1":
            tls_config["insecure"] = True
        alpn = params.get("alpn")
        if alpn:
            tls_config["alpn"] = [
                x.strip() for x in unquote(alpn).split(",") if x.strip()
            ]
        fp = params.get("fp")
        if fp:
            tls_config["utls"] = {"enabled": True, "fingerprint": fp}
        if security == "reality":
            tls_config["reality"] = {
                "enabled": True,
                "public_key": params.get("pbk", ""),
                "short_id": params.get("sid", ""),
            }
        outbound["tls"] = tls_config

    # 3. 处理传输层 (Transport)
    net_type = params.get("type", "tcp")
    if net_type == "ws":
        ws_config: dict[str, Any] = {
            "type": "ws",
            "path": unquote(params.get("path", "/")),
        }
        host = params.get("host")
        if host:
            ws_config["headers"] = {"Host": host}
        outbound["transport"] = ws_config
    elif net_type == "grpc":
        outbound["transport"] = {
            "type": "grpc",
            "service_name": unquote(params.get("serviceName", "")),
        }
    elif net_type == "httpupgrade":
        hu_config = {
            "type": "httpupgrade",
            "path": unquote(params.get("path", "/")),
        }
        host = params.get("host")
        if host:
            hu_config["host"] = host
        outbound["transport"] = hu_config
    return outbound
