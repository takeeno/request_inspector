from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import os
import json

app = FastAPI()

def force_serializable(obj):
  """
  bytes, tuple, setなど、JSONにできないあらゆる型を
  再帰的にスキャンして安全な型（str, list, dict）に変換する
  """
  if isinstance(obj, bytes):
    return obj.decode('latin-1', errors='ignore')
  if isinstance(obj, (list, tuple, set)):
    return [force_serializable(item) for item in obj]
  if isinstance(obj, dict):
    return {
      (k.decode('latin-1', errors='ignore') if isinstance(k, bytes) else str(k)): force_serializable(v)
      for k, v in obj.items()
    }
  if isinstance(obj, (str, int, float, bool, type(None))):
    return obj
  return str(obj)

@app.get("/")
async def ultra_stable_check(request: Request):
  try:
    scope = request.scope
    
    # ボディ読み取り
    body_str = ""
    try:
      # タイムアウト等で読み取れない場合に備える
      body_bytes = await request.body()
      body_str = body_bytes.decode('utf-8', errors='ignore')
    except Exception:
      body_str = "[Body not readable]"

    # すべての情報を構築
    raw_data = {
      "summary": {
        "method": request.method,
        "url": str(request.url),
        "client": list(request.client) if request.client else None,
      },
      "parsed_headers": dict(request.headers),
      "cookies": dict(request.cookies),
      "query_params": dict(request.query_params),
      # ここで scope 全体を完全にクリーンアップする
      "asgi_scope": force_serializable(scope),
      "body": body_str
    }

    return JSONResponse(content=raw_data)

  except Exception as e:
    # 最後の砦：ここでもエラーが出る場合は文字列として返す
    return JSONResponse(
      status_code=500,
      content={"error": "Serialization failed", "msg": str(e)}
    )

if __name__ == "__main__":
  port = int(os.environ.get("PORT", 8000))
  uvicorn.run(app, host="0.0.0.0", port=port)
