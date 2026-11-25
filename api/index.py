from fastapi import FastAPI, HTTPException, Query, Header
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
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {e}")
