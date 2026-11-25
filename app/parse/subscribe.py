import base64
import re
from app import config, requests
from app import Path


def is_base64(sub_base64: str) -> str | None:
    # 去掉首尾及内部可能存在的换行符
    cleaned = "".join(sub_base64.split())
    if not cleaned:
        return None
    # 兼容标准 Base64 (+/) 和 URL-safe Base64 (-_)
    if not re.match(r"^[A-Za-z0-9+/_-]+={0,2}$", cleaned):
        return None
    # 自动补齐缺失的 '=' 填充
    padded = cleaned + "=" * (-len(cleaned) % 4)
    try:
        base64.urlsafe_b64decode(padded.encode("ascii"))
        return padded
    except Exception:
        return None


def main(sub: str, allow_local_file: bool = True):
    agreement = ("vless://", "trojan://", "ss://", "vmess://", "hysteria2://")
    sub = sub.strip()
    if sub.startswith(("http://", "https://")):
        try:
            response = requests.get(sub, headers={"User-Agent": config.UA}, timeout=10)
            response.raise_for_status()
            sub = response.text.strip()
        except Exception as e:
            raise requests.HTTPError(f"订阅链接请求失败: {e}")
    if sub.startswith(agreement):
        return sub
    # Web 接口模式下禁用本地文件路径读取，防止任意文件读取漏洞
    if allow_local_file and len(sub) < 260 and Path(sub).is_file():
        with open(sub, "r", encoding="utf-8") as f:
            sub_data = f.read()
            if sub_data.startswith(agreement):
                return sub_data
            b64_str = is_base64(sub_data)
    else:
        b64_str = is_base64(sub)
    if b64_str is None:
        raise ValueError(f"无法识别订阅数据，请检查 {config.UPLAD_UA}")
    return base64.urlsafe_b64decode(b64_str).decode("utf-8-sig").strip()
