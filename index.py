import traceback
from fastapi import FastAPI, HTTPException, Query, Header
from app import requests
from app.run import generate_config

app = FastAPI()


@app.get("/sb")
def get_singbox_config(
    s: str = Query(..., description="订阅链接、节点文本或Base64字符串"),
    f: str = Query("", description="模板编号、文件名或远程模板URL"),
    user_agent: str = Header(default=""),
):
    try:
        return generate_config(sub_input=s, input_temp=f, header=user_agent)
    except (ValueError, requests.HTTPError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        traceback.print_exc()  # 在 Vercel Logs 中输出完整报错行号
        raise HTTPException(
            status_code=500, detail=f"服务器内部错误: {type(e).__name__}: {e}"
        )
