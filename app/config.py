from app import Path

# 基于当前 config.py 所在目录定位 template，确保 Vercel 环境下路径绝对准确
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPDIR = BASE_DIR / "template"
DEFAULT_TEMP = TEMPDIR / "base.json"
OUT_CONFIG = BASE_DIR / "config.json"
TEMP_OK: Path = DEFAULT_TEMP

UPLAD_UA = ""
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:160.0) Gecko/20100101 Firefox/160.0"

# 删除过滤标志
FLAG = True
# 运行时状态变量（每次请求前由 generate_config 覆盖重置）
##  数据存储
TEMP_DATA: dict = {}
SINGBOX_CONFIG: dict = {}

SUBSCRIPTION: str = ""
NODE: list = []
DEBUG = False
DIRECT_OUTBOUNDS = {"tag": "Direct ☘️", "type": "direct", "udp_fragment": True}
