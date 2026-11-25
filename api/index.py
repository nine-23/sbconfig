from fastapi import FastAPI, HTTPException, Query, Header
from app.run import generate_config

app = FastAPI()


@app.get("/api/sub")
def get_singbox_config(
    sub: str = Query(..., description="订阅链接、节点文本或Base64字符串"),
    temp: str = Query("", description="模板编号、文件名或远程模板URL"),
    user_agent: str | None = Header(default=None),
):
    try:
        return generate_config(sub_input=sub, input_temp=temp, header=user_agent)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {e}")
